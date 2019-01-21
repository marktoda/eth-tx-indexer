import json


class __Config:
	def __init__(self):
		with open('config.json', 'r') as f:
			self.config: dict = json.loads(f.read())

	def get(self) -> dict:
		return self.config


config = __Config().get()
