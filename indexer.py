"""
Runs the indexing program to get ethereum blockchain statistics
"""
import math
import time
from threading import Thread
import logging

from config import config
from blockchain.rpc.blockchain import Block
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

	def continuously_index(self):
		"""
		Runs the indexer to fill in transactions in the past and new ones as they come in
		"""
		our_chainhead = Transaction.get_latest_block_number()
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
			thread = Thread(target=self.index, args=(previous, network_chainhead), daemon=True)
			thread.start()

	def index(self, start_block, end_block) -> None:
		"""
		Gets blockchain data for the range of blocks from start_block to the current chainhead
		:param start_block: The block to start indexing at
		:param end_block the block to end indexing at
		"""
		logging.info(f"Indexing from block {start_block} to block {end_block}")
		for block_number in range(start_block, end_block):
			try:
				block: Block = self.blockchain.get_block(block_number)
				logging.info(f"Indexing {len(block)} transactions in block {block_number}")
				for tx in block:
					tx.save()
			except Exception as e:
				continue


idx = Indexer()
idx.continuously_index()
idx.index(7000000, 7000010)
