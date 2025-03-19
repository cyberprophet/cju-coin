import hashlib

from src import config, db
from src.models import Block, Transaction
from src.utils import blockchain_util

from ecdsa import NIST256p, VerifyingKey


class Transfer:
    def __init__(
        self,
        send_public_key: str,
        send_blockchain_addr: str,
        recv_blockchain_addr: str,
        amount: float,
        signature: str = None,
    ):
        self.send_public_key = send_public_key
        self.send_blockchain_addr = send_blockchain_addr
        self.recv_blockchain_addr = recv_blockchain_addr
        self.amount = amount
        self.block_id = (
            Block.query.filter(Block.timestamp)
            .order_by(Block.timestamp.desc())
            .first()
            .id
        )
        self.signature = signature

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
        transaction = blockchain_util.sorted_dict_by_key(
            {
                "send_blockchain_addr": self.send_blockchain_addr,
                "recv_blockchain_addr": self.recv_blockchain_addr,
                "amount": float(self.amount),
            }
        )

        if self.send_blockchain_addr == config.BLOCKCHAIN_NETWORK:
            self.commit_transaction()
            return True

        is_verified = self.verify_transaction_signature(
            self.send_public_key,
            self.signature,
            transaction,
        )

        if is_verified:
            self.commit_transaction()

        return is_verified

    def verify_transaction_signature(
        self,
        send_public_key: str,
        signature: str,
        transaction: dict,
    ) -> bool:
        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode("utf-8"))

        message = sha256.digest()

        signature_byte = bytes().fromhex(signature)

        verifying_key = VerifyingKey.from_string(
            bytes().fromhex(send_public_key),
            curve=NIST256p,
        )

        try:
            is_verified = verifying_key.verify(
                signature=signature_byte,
                data=message,
            )
            return is_verified

        except Exception as e:
            return False
