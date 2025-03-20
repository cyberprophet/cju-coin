import hashlib
import json

from src import config
from src.models import Block, Transaction


def sorted_dict_by_key(unsorted_dic: dict):
    return dict(sorted(unsorted_dic.items()))


def get_blockchain():
    blockchain_exist = Block.query.all()

    if not blockchain_exist:
        from src.blockchain import BlockChain

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


def get_prev_hash() -> str:
    prev_hash = (
        Block.query.filter(Block.timestamp)
        .order_by(Block.timestamp.desc())
        .first()
        .prev_hash
    )
    return prev_hash


def valid_proof(nonce: int, prev_hash: str, transactions: list) -> bool:
    guess_block = sorted_dict_by_key(
        {
            "transactions": transactions,
            "nonce": nonce,
            "prev_hash": prev_hash,
        }
    )
    guess_block_hash = hash(guess_block)

    result = (
        guess_block_hash[: config.MINING_DIFFICULTY] == "0" * config.MINING_DIFFICULTY
    )
    return result
