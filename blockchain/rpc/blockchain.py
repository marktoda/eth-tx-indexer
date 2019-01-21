"""
Base class for Ethereum blockchain information
"""

import json
from typing import List
import logging
import requests

from blockchain.hexdata import Hexdata
from blockchain.transaction import Transaction

Block = List[Transaction]


class Blockchain():
	GET_BLOCK_METHOD = "eth_getBlockByNumber"
	GET_TRANSACTION_RECEIPT_METHOD = "eth_getTransactionReceipt"

	def __init__(self, endpoint: str = "localhost:8545"):
		self.endpoint = endpoint

	def make_json_rpc_call(self, method: str, params: List):
		"""
		Makes a JSON-RPC call
		:param method: The JSON-RPC method to call
		:param params: List of parameters to send along with the request
		:return: The correctly formatted
		"""
		data = {
			"jsonrpc": "2.0",
			"method": method,
			"params": params,
			"id": 1
		}
		headers = {
			"Content-Type": "application/json"
		}
		res = requests.post(self.endpoint, data=json.dumps(data), headers=headers)
		if not res.status_code == 200 or "result" not in res.json():
			raise Exception(f'Invalid json result from {self.endpoint}: {res.text}')
		return res.json()["result"]

	def get_latest_block_number(self) -> int:
		"""
		Gets the most recent block's number (i.e. chainhead height)
		:return: The number of the most recent block
		"""
		block = self.make_json_rpc_call(Blockchain.GET_BLOCK_METHOD, ["latest", False])
		if "number" not in block:
			raise Exception(f'Invalid latest block from {self.endpoint}: {block}')
		return int(block["number"], 16)

	def get_block(self, number: int) -> Block:
		"""
		Gets a block by its block height
		:param number: The block height of the block to get
		:return: The list of transactions in the block, returns None if number is past chainhead
		"""
		block = self.make_json_rpc_call(Blockchain.GET_BLOCK_METHOD, [hex(number), True])
		if "transactions" not in block:
			logging.error(f'Invalid block at height {number} from {self.endpoint}: {block}')
		result_block: Block = []
		for tx in block["transactions"]:
			tx = Transaction.from_json(tx)
			if tx.is_contract_call() or tx.is_contract_deployment():
				tx.insert_tx_receipt_data(self.get_transaction_receipt(tx.get_txid()))
			result_block.append(tx)
		return result_block

	def get_transaction_receipt(self, txid: Hexdata) -> List[List[Hexdata]]:
		"""
		Gets the transaction event logs for a given txid
		:param txid: The txid to get logs for
		:return: The list of events from that txid, each of which has a list of logs
		"""
		tx_receipt = self.make_json_rpc_call(Blockchain.GET_TRANSACTION_RECEIPT_METHOD, [txid.get()])
		if "logs" not in tx_receipt or "gasUsed" not in tx_receipt:
			logging.error(f"Invalid tx receipt for txid {txid.get()}: {tx_receipt}")
		return tx_receipt
