"""
Class to represent an Ethereum transaction
"""
from typing import List

import pymongo
import logging

from blockchain.hexdata import Hexdata
from blockchain.transaction import Transaction
from mongo import db

db.blocks.create_index('height')


class Block:
	db = db.blocks

	def __init__(self, height: int, num_transactions: int, block_hash: Hexdata, transactions: List[Transaction]):
		self.height = height
		self.num_transactions = num_transactions
		self.block_hash = block_hash
		self.transactions: List[Transaction] = transactions

	def get_transactions(self) -> List[Transaction]:
		return self.transactions

	def get_hash(self) -> Hexdata:
		return self.block_hash

	# db things

	def save(self) -> None:
		"""
		Saves this block to the mongo db
		"""
		existing = Block.db.find_one({"height": self.height})
		if existing:
			logging.info(f"Already have a block at height {self.height}")
			return
		model = {
			"height": self.height,
			"num_transactions": self.num_transactions,
			"block_hash": self.block_hash.get()
		}
		Block.db.insert_one(model)

	@staticmethod
	def from_json(json_obj: dict):
		transactions: List[Transaction] = []
		for tx in json_obj["transactions"]:
			tx = Transaction.from_json(tx)
			transactions.append(tx)
		block_hash = Hexdata(json_obj["hash"])
		number = int(json_obj["number"], 16)
		num_transactions = len(transactions)
		return Block(number, num_transactions, block_hash, transactions)

	@staticmethod
	def get_latest_block_number() -> int:
		recent_block = Block.db.find({}).sort("height", pymongo.DESCENDING).limit(1)
		if recent_block.count() == 0:
			chainhead = 0
		else:
			recent_block = recent_block[0]
			chainhead = recent_block["height"]
		logging.info(f"DB Chainhead: {chainhead}")
		return chainhead

	@staticmethod
	def has_block(number: int) -> bool:
		block = Block.db.find_one({"height": number})
		return True if block else False

	@staticmethod
	def get_block(number:  int):
		"""
		Returns block object for the given height without the contained transactions
		:param number: Height of block to get
		:return: Block object
		"""
		block = Block.db.find_one({"height": number})
		if not block:
			raise Exception(f'No block at height {number}')
		return Block(number, Transaction.db.count({"height": number}), Hexdata(block["block_hash"]), [])

	@staticmethod
	def remove_block(number: int) -> None:
		"""
		Removes the block with the given height from the db
		:param number: The block height to remove
		"""
		Block.db.remove({"height": number})
