"""
Class to represent an Ethereum transaction
"""
import pymongo
import logging

from .address import Address
from .amount import Amount
from .hexdata import Hexdata
from mongo import db

db.transactions.create_index('txid')
db.transactions.create_index('sender')
db.transactions.create_index('recipient')
db.transactions.create_index('height')


class Transaction:
	db = db.transactions
	KNOWN_METHOD_IDS = {
		"0xa9059cbb": "Token transfer",
		"0x39125215": "BitGo send"
	}

	def __init__(
			self, height: int, txid: Hexdata, sender: Address, recipient: Address, amount: Amount,
			gas_price: int, gas: int, data: Hexdata = None
	):
		self.successful = True
		self.height = height
		self.txid = txid
		self.sender: Address = sender
		self.recipient: Address = recipient
		self.amount: Amount = amount
		self.gas_price = gas_price
		self.gas = gas
		self.data: Hexdata = data
		self.topics = []
		self.contract_created = None

	def get_txid(self) -> Hexdata:
		return self.txid

	def is_contract_deployment(self) -> bool:
		return self.recipient.is_null_address()

	def is_contract_call(self) -> bool:
		return True if self.data and not self.is_contract_deployment() else False

	def contract_call_type(self) -> str:
		method_id: str = self.data.get()[:10]
		if method_id in Transaction.KNOWN_METHOD_IDS:
			return Transaction.KNOWN_METHOD_IDS[method_id]
		else:
			return method_id

	def insert_tx_receipt_data(self, tx_receipt: dict) -> None:
		"""
		Inserts data from the transaction receipt
		:param tx_receipt: An object containing topics array, gas used, status code, deployed contract
		"""
		result_logs = []
		for log in tx_receipt["logs"]:
			this_log = []
			for topic in log["topics"]:
				this_log.append(topic)
			result_logs.append(this_log)
		self.topics = result_logs
		if self.is_contract_deployment():
			self.contract_created = tx_receipt["contractAddress"]
		if "status" in tx_receipt:
			self.successful = tx_receipt["status"] == "0x1"
		self.gas = int(tx_receipt["gasUsed"], 16)

	@staticmethod
	def from_json(json_obj: dict):
		height = int(json_obj["blockNumber"], 16)
		txid = Hexdata(json_obj["hash"])
		sender = Address(json_obj["from"])
		recipient = Address(json_obj["to"])
		amount = Amount(int(json_obj["value"], 16))
		gas = int(json_obj["gas"], 16)
		gas_price = int(json_obj["gasPrice"], 16)
		data = None
		if "input" in json_obj and len(json_obj["input"]) > 2:
			data = Hexdata(json_obj["input"])
		return Transaction(height, txid, sender, recipient, amount, gas_price, gas, data)

	@staticmethod
	def remove_transactions(height: int) -> None:
		Transaction.db.remove({"height": height})

	# db things

	def save(self):
		"""
		Saves this transaction to the mongo db
		"""
		existing = Transaction.db.find_one({"txid": self.txid.get()})
		if existing:
			logging.info(f"Already have a transaction with txid {self.txid.get()}")
			return
		model = {
			"height": self.height,
			"txid": self.txid.get(),
			"sender": self.sender.get(),
			"recipient": self.recipient.get(),
			"amount": self.amount.get(),
			"gas_price": self.gas_price,
			"gas": self.gas,
			"is_contract_deployment": self.is_contract_deployment(),
			"is_contract_call": self.is_contract_call(),
			"topics": self.topics,
			"successful": self.successful
		}
		if self.is_contract_call():
			model["contract_function"] = self.contract_call_type()
		if self.is_contract_deployment():
			model["contract_created"] = self.contract_created
		Transaction.db.insert_one(model)
