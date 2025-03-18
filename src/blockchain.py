import time

from src import db
from src.models import Block
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
            prev_hash=blockchain_util.hash({}), nonce=0, timestamp=time.time()
        )

        db.session.add(genesis_block)
        db.session.commit()

        return True

    def create_block(self, nonce: int, prev_hash: str = None):
        try:
            db.session.add(
                Block(prev_hash=prev_hash, nonce=nonce, timestamp=time.time())
            )
            db.session.commit()

        except Exception as e:
            print("Fail to block on database")
            print(f"Error: {e}")

            return False
