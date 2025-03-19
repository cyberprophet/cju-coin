import hashlib
import json

from src.blockchain import BlockChain
from src.models import Block, Transaction


def sorted_dict_by_key(unsorted_dic: dict):
    return sorted(unsorted_dic.items())


def get_blockchain():
    blockchain_exist = Block.query.all()

    if not blockchain_exist:
        blockchain = BlockChain()
        blockchain.create_genesis_block()

    return build_blockchain_json()


def build_blockchain_json() -> dict:
    blocks = Block.query.filter(Block.timestamp).order_by(Block.timestamp)

    result_dic = {"chain": [], "transaction_pool": []}

    for block in blocks:
        result_dic["chain"].append(
            {
                "nonce": block.nonce,
                "prev_hash": block.prev_hash,
                "timestamp": block.timestamp,
                "transactions": get_transaction_list(block),
            }
        )
    last_block = (
        Block.query.filter(Block.timestamp).order_by(Block.timestamp.desc()).first()
    )

    result_dic["transaction_pool"] = get_transaction_list(last_block)

    return result_dic


def get_transaction_list(block: Block) -> list:
    transaction_exist = Transaction.query.all()

    if not transaction_exist:
        return []

    transaction_list = []
    transactions = block.transactions

    for transaction in transactions:
        transaction_list.append(
            {
                "send_blockchain_addr": transaction.send_addr,
                "recv_blockchain_addr": transaction.recv_addr,
                "amount": transaction.amount,
            }
        )
    return transaction_list


def hash(block: dict):
    sorted_block = json.dumps(block, sort_keys=True)

    return hashlib.sha256(sorted_block.encode()).hexdigest()


def calculate_total_amount(blockchain_addr: str) -> float:
    total_amount = 0.0

    chain = get_blockchain()

    for block in chain["chain"]:
        for transaction in block["transactions"]:
            value = float(transaction["amount"])

            if blockchain_addr == transaction["recv_blockchain_addr"]:
                total_amount += value

            if blockchain_addr == transaction["send_blockchain_addr"]:
                total_amount -= value

    return total_amount
