import os
from src.secret import csrf_token_secret

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(BASE_DIR, "blockchain.db"))

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = csrf_token_secret

BLOCKCHAIN_NETWORK = "BLOCK CHAIN NETWORK"

MINING_DIFFICULTY = 5

MINING_REWORD = 15.0
