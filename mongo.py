from pymongo import MongoClient

from config import config

mongo_client = MongoClient(config["mongo"]["host"])
db = mongo_client[config["mongo"]["db"]]
