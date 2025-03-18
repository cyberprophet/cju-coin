from src import db
from src.models import Block, Transaction


class Transfer:
    def __init__(
        self,
        send_blockchain_addr: str,
        recv_blockchain_addr: str,
        amount: float,
    ):
        self.send_blockchain_addr = send_blockchain_addr
        self.recv_blockchain_addr = recv_blockchain_addr
        self.amount = amount
        self.block_id = (
            Block.query.filter(Block.timestamp)
            .order_by(Block.timestamp.desc())
            .first()
            .id
        )

    def commit_transaction(self):
        transaction = Transaction(
            block_id=self.block_id,
            send_addr=self.send_blockchain_addr,
            recv_addr=self.recv_blockchain_addr,
            amount=float(self.amount),
        )
        db.session.add(transaction)
        db.session.commit()

    def add_transaction(self) -> bool:
        is_verified = True

        if is_verified:
            self.commit_transaction()
            return True

        return False
