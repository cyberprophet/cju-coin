import time
import requests

from typing import List

from src import config, db
from src.models import Block, Transaction
from src.utils import blockchain_util


class BlockChain:
    def __init__(self):
        pass

    def create_genesis_block(self) -> bool:
        block_exist = Block.query.all()

        if block_exist:
            print(
                {
                    "status": "Fail to create genesis block",
                    "error": "Block aleady exist",
                }
            )
            return False

        genesis_block = Block(
            prev_hash=blockchain_util.hash({}),
            nonce=0,
            timestamp=time.time(),
        )

        db.session.add(genesis_block)
        db.session.commit()

        return True

    def create_block(self, nonce: int, prev_hash: str = None):
        try:
            db.session.add(
                Block(
                    prev_hash=prev_hash,
                    nonce=nonce,
                    timestamp=time.time(),
                )
            )
            db.session.commit()

        except Exception as e:
            print("Fail to block on database")
            print(f"Error: {e}")

            return False

    def vaild_chain(self, chain: List[dict]) -> bool:
        prev_block = chain[0]

        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block["prev_hash"] != blockchain_util.hash(prev_block):
                return False

            if not blockchain_util.valid_proof(
                nonce=int(block["nonce"]),
                prev_hash=prev_block["prev_hash"],
                transactions=prev_block["transactions"],
            ):
                return False

            prev_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        longest_chain = None

        my_chain = blockchain_util.get_blockchain()["chain"]

        max_length = len(my_chain)

        url = f"http://{config.MY_PUBLIC_IP}:{config.PORT_P2P}/neighbors"

        response = requests.get(url)

        neighbors_dic = response.json()

        for neighbor in neighbors_dic.values():
            ip = neighbor["ip"]

            if ip == config.MY_PUBLIC_IP:
                continue

            neighbor_url = f"http://{ip}:{config.PORT_MINING}/get-chain"

            try:
                resp_get_chain = requests.get(neighbor_url)

                if resp_get_chain.status_code == 200:
                    blockchain = resp_get_chain.json()
                    chain = blockchain["chain"]
                    chain_length = len(chain)

                    if chain_length > max_length and self.vaild_chain(chain):
                        max_length = chain_length
                        longest_chain = chain

            except Exception as e:
                print(f"Cannot connect to {neighbor_url}")

        if longest_chain:
            blocks = Block.query.all()

            for block in blocks:
                db.session.delete(block)
                db.session.commit()

            transactions = Transaction.query.all()

            for transaction in transactions:
                db.session.delete(transaction)
                db.session.commit()

            for block_in_chain in longest_chain:
                block = Block()
                block.prev_hash = block_in_chain["prev_hash"]
                block.nonce = block_in_chain["nonce"]
                block.timestamp = block_in_chain["timestamp"]

                db.session.add(block)
                db.session.commit()

                for transaction_in_block in block_in_chain["transactions"]:
                    transaction_new = Transaction()
                    transaction_new.block_id = block.id
                    transaction_new.send_addr = transaction_in_block[
                        "send_blockchain_addr"
                    ]
                    transaction_new.recv_addr = transaction_in_block[
                        "send_blockchain_addr"
                    ]
                    transaction_new.amount = transaction_in_block["amount"]

                    db.session.add(transaction_new)
                    db.session.commit()

            print("resolve_conflicts: chain replaced.")
            return True

        return False
