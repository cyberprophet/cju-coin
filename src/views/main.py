from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
)
from src.transfer import Transfer
from src.utils.blockchain_util import calculate_total_amount, get_blockchain

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
            send_public_key=request_json.get("send_public_key"),
            send_blockchain_addr=request_json.get("send_blockchain_addr"),
            recv_blockchain_addr=request_json.get("recv_blockchain_addr"),
            amount=request_json.get("amount"),
            signature=request_json.get("signature"),
        )
        is_transacted = transfer.add_transaction()

        if not is_transacted:
            return jsonify({"status": "fail"}), 400

        return jsonify({"status": "success"}), 201


@bp.route("/coin_amount/", methods=["GET", "POST"])
def coin_amount():
    """코인 갯수를 계산하여 json 리턴"""
    json_data = request.json
    
    blockchain_addr = json_data["blockchain_addr"]

    if not blockchain_addr:
        return (
            jsonify(
                {
                    "status": "fail",
                    "content": "지갑주소(blockchain address)가 없습니다.",
                }
            ),
            400,
        )
    return (
        jsonify(
            {"status": "succcess", "content": calculate_total_amount(blockchain_addr)}
        ),
        201,
    )
