from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
)
from src.transfer import Transfer
from src.utils.blockchain_util import get_blockchain

bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@bp.route("/get-chain", methods=["GET"])
def get_chain():
    block_chain = get_blockchain()
    response = {"chain": block_chain.get("chain")}

    return jsonify(response), 200


@bp.route("/transactions", methods=["GET", "POST"])
def transactions():
    block_chain = get_blockchain()

    if request.method == "GET":
        resp = {
            "transactions": block_chain.get("transaction_pool"),
            "length": len(block_chain.get("transaction_pool")),
        }
        return jsonify(resp), 200

    if request.method == "POST":
        request_json = request.json
        transfer = Transfer(
            send_blockchain_addr=request_json.get("send_blockchain_addr"),
            recv_blockchain_addr=request_json.get("recv_blockchain_addr"),
            amount=request_json.get("amount"),
        )
        is_transacted = transfer.add_transaction()

        if not is_transacted:
            return jsonify({"status": "fail"})

        return jsonify({"status": "success"})
