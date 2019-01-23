"""
Runs the indexing program to get ethereum blockchain statistics
"""
import math
import time
from threading import Thread
import logging

from blockchain.block import Block
from config import config
from blockchain.rpc.infura import Infura

from blockchain.transaction import Transaction


class Indexer:
	def __init__(self):
		self.blockchain = Infura()
		logging.basicConfig(
			filename=config["logging"]["file"],
			level=logging.INFO,
			format='%(asctime)s %(levelname)-8s %(message)s',
			datefmt='%Y-%m-%d %H:%M:%S'
		)
		self.block_threads = config["indexer"]["loader_threads"]
		self.chainhead_sleep_time_s = config["indexer"]["chainhead_wait_time_s"]

	def continuously_index(self) -> None:
		"""
		Runs the indexer to fill in transactions in the past and new ones as they come in
		"""
		our_chainhead =0 # Block.get_latest_block_number()
		network_chainhead = self.blockchain.get_latest_block_number()
		# Round up as it never hurts to do more than necessary
		blocks_per_thread = math.ceil((network_chainhead - our_chainhead) / self.block_threads)

		for i in range(self.block_threads):
			start = our_chainhead + (i * blocks_per_thread)
			end = our_chainhead + ((i + 1) * blocks_per_thread)
			thread = Thread(target=self.index, args=(start, end), daemon=True)
			thread.start()

		while True:
			# wait a lil bit for more blocks to come in
			time.sleep(self.chainhead_sleep_time_s)
			previous = network_chainhead
			network_chainhead = self.blockchain.get_latest_block_number()

			# check if our old chainhead is still correct, if not... fix reorg
			if Block.has_block(previous):
				block = Block.get_block(previous)
				our_block_hash = block.get_hash().get()
				network_block = self.blockchain.get_block(previous)
				network_block_hash = network_block.get_hash().get()
				if network_block_hash != our_block_hash:
					previous = self.handle_reorg(previous)

			thread = Thread(target=self.index, args=(previous, network_chainhead), daemon=True)
			thread.start()

	def index(self, start_block: int, end_block: int) -> None:
		"""
		Gets blockchain data for the range of blocks from start_block to the current chainhead
		:param start_block: The block to start indexing at
		:param end_block the block to end indexing at
		"""
		logging.info(f"Indexing from block {start_block} to block {end_block}")
		for block_number in range(start_block, end_block):
			if not Block.has_block(block_number):
				try:
					block: Block = self.blockchain.get_block(block_number)
					logging.info(f"Indexing {len(block.get_transactions())} transactions in block {block_number}")
					for tx in block.get_transactions():
						tx.save()
					block.save()
				except Exception as e:
					continue
			else:
				logging.info(f"Already indexed block {block_number}")

	def handle_reorg(self, last_number: int) -> int:
		"""
		Handles an Ethereum reorganization
		:param last_number: Last number in our db that is knwown to be reorged out
		:return new db height -- place to start indexing from again
		"""
		height = last_number
		block = Block.get_block(height)
		our_block_hash = block.get_hash().get()
		network_block = self.blockchain.get_block(height)
		network_block_hash = network_block.get_hash().get()
		# keep going back from last_number until we find a block where we're correct with the network
		while our_block_hash != network_block_hash:
			Block.remove_block(height)
			Transaction.remove_transactions(height)
			height -= 1
			block = Block.get_block(height)
			our_block_hash = block.get_hash().get()
			network_block = self.blockchain.get_block(height)
			network_block_hash = network_block.get_hash().get()
		logging.info(f"Removed transactions for reorganization from block {last_number} to block {height}")
		return height


idx = Indexer()
idx.continuously_index()