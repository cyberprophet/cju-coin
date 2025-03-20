import os
import requests

from src.secret import csrf_token_secret

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(BASE_DIR, "blockchain.db"))

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = csrf_token_secret

BLOCKCHAIN_NETWORK = "BLOCK CHAIN NETWORK"

MINING_DIFFICULTY = 5

MINING_REWARD = 15.0

STOP_MINING = True

# 자신의 공인 아이피를 확인하기 위해 이용하는 서비스 프로바이더
# Other possible service providers
#   - https://ident.me
#   - https://api.ipify.org
#   - https://myip.dnsomatic.com
IP_CHECK_SERVICE_PROVIDER = "https://checkip.amazonaws.com"

# My Host Information
MY_PUBLIC_IP = requests.get(IP_CHECK_SERVICE_PROVIDER).text.strip()

# Seed Node IP addr
SEED_NODE_IP = "127.0.0.1"

# P2P Network Port Number
PORT_P2P = "22901"

# Mining node Port #
PORT_MINING = "39456"

MINING_ACTIVE = False
