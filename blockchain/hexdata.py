"""
Class to represent Ethereum smart contract data and transactionids
"""


class Hexdata:
	def __init__(self, data: str):
		if not data.startswith('0x'):
			data = '0x' + data
		self.data: str = data.lower()

	def get(self):
		return self.data
