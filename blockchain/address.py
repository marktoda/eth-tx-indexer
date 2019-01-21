"""
Class to represent an Ethereum address
"""
from typing import Optional


class Address:
	def __init__(self, address: Optional[str]):
		if not address:
			self.is_null = True
			self.address = "0x0000000000000000000000000000000000000000"
		else:
			if not address.startswith('0x'):
				address = '0x' + address
			if not len(address) == 42:
				raise Exception(f'Invalid address {address}')
			self.address: str = address.lower()
			self.is_null = False

	def get(self) -> str:
		return self.address

	def is_null_address(self) -> bool:
		return self.is_null
