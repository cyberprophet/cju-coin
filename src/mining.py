import threading
import requests

from typing import List, Tuple

from src import config, create_app
from src.utils import blockchain_util
from src.transfer import Transfer
from src.config import BLOCKCHAIN_NETWORK, MINING_DIFFICULTY, MINING_REWARD
from src.blockchain import BlockChain


class Mine:
    def __init__(
        self,
        difficulty: int = MINING_DIFFICULTY,
        reward: float = MINING_REWARD,
    ) -> None:
        self.difficulty = difficulty
        self.reward = reward

    def proof_of_work(self, transaction_pool: List[dict]) -> int:
        nonce: int = 0

        prev_hash = blockchain_util.get_prev_hash()

        while blockchain_util.valid_proof(transaction_pool, prev_hash, nonce) is False:
            nonce += 1

        return nonce

    def mining(self, recv_blockchain_addr) -> Tuple[bool, str]:
        app = create_app()

        with app.app_context():
            transfer = Transfer(
                send_public_key="",
                send_blockchain_addr=BLOCKCHAIN_NETWORK,
                recv_blockchain_addr=recv_blockchain_addr,
                amount=self.reward,
            )
            transfer.add_transaction()

            prev_block = blockchain_util.get_blockchain().get("chain")[-1]

            transaction_pool_after_add_transaction = prev_block["transactions"]

            nonce = self.proof_of_work(transaction_pool_after_add_transaction)

            prev_block_sorted = blockchain_util.sorted_dict_by_key(prev_block)

            prev_hash = blockchain_util.hash(prev_block_sorted)

            blockchain_obj = BlockChain()
            blockchain_obj.create_block(
                nonce=nonce,
                prev_hash=prev_hash,
            )
            print("채굴 성공!")

            url = f"http://{config.MY_PUBLIC_IP}:{config.PORT_P2P}/neighbors"

            response = requests.get(url)

            neighbors_dic = response.json()

            for neighbor in neighbors_dic.values():
                json_data = {"ip": config.MY_PUBLIC_IP, "port": config.PORT_P2P}
                try:
                    url_update = f'http://{neighbor["ip"]}:{config.PORT_P2P}/update'

                    response = requests.get(url_update, params=json_data, timeout=3)

                    if response.status_code != 200:
                        print(f"Sync neighbor fail on {url_update}")

                except:
                    print(f"Sync process failed")

            response = requests.get(url)

            neighbors_dic = response.json()

            for neighbor in neighbors_dic.values():
                ip, port = neighbor["ip"], neighbor["port"]

                if ip == config.MY_PUBLIC_IP and port == config.PORT_P2P:
                    continue

                neighbor_url = f"http://{ip}:{config.PORT_MINING}/resolve_conflict"

                try:
                    res_resolve = requests.get(neighbor_url)

                    if res_resolve.status_code == 200:
                        print("Success resolve conflict")

                except:
                    print(f"Cannot connect to {neighbor_url}")
                    return (False, "fail")

            return (True, "success")

    def start_mining(self, recv_blockcain_addr: str) -> None:
        """연속적으로 채굴(마이닝) 수행"""

        def mining_thread():
            while True:
                self.mining(recv_blockcain_addr)

                if config.STOP_MINING:
                    print("코인 채굴을 중단합니다. in Mining.start_mining")
                    config.STOP_MINING = False
                    break

        trd = threading.Thread(target=mining_thread)
        trd.daemon = True  #  메인 프로그램이 중지되면 백그라운드 채굴도 중단
        trd.start()
