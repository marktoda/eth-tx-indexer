"""
Class to represent amounts of Ether and tokens
"""


class Amount:
	base_units = {
		"ETH": 18
	}

	def __init__(self, amount: int, coin: str = "ETH"):
		"""
		Initialize amount
		:param amount: The amount of the coin in base units
		:param coin: The coin to get
		"""
		self.amount = amount
		self.coin = coin

	def get(self) -> str:
		"""
		Returns the amount in full units (i.e. ETH)
		:return: The amount
		"""
		return str(self.amount)
