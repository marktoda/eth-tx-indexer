"""
Class to get blockchain data from Infura
"""

from config import config
from .blockchain import Blockchain


class Infura(Blockchain):
	def __init__(self):
		super(Infura, self).__init__(config["infura"]["endpoint"])
