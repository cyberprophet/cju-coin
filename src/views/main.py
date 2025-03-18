from flask import Blueprint, jsonify

from src.utils.blockchain_util import get_blockchain

bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def home():
    return "hello world"


@bp.route("/get-chain", methods=["GET"])
def get_chain():
    block_chain = get_blockchain()
    response = {"chain": block_chain.get("chain")}

    return jsonify(response), 200
