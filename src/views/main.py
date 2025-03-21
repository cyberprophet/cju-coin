import threading

from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
)
from src import config
from src.blockchain import BlockChain
from src.mining import Mine
from src.transfer import Transfer
from src.utils.blockchain_util import calculate_total_amount, get_blockchain

bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def home():
    return render_template("mining.html")


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
            {"status": "success", "content": calculate_total_amount(blockchain_addr)}
        ),
        201,
    )


@bp.route("/mining", methods=["GET", "POST"])
def mining():
    if request.method == "GET":
        recv_blockchain_addr = request.args.get("blockchain_addr")

    if request.method == "POST":
        json_data = request.json

        recv_blockchain_addr = json_data["blockchain_addr"]

    mine = Mine()
    mine.difficulty

    mining_success, _ = mine.mining(recv_blockchain_addr)

    if mining_success:
        return jsonify({"status": "success", "reward": config.MINING_REWARD}), 200

    return jsonify({"status": "fail", "reason": "fail to mining"}), 200


@bp.route("/mining/start", methods=["POST"])
def mining_start():
    """연속채굴 시작"""
    config.MINING_ACTIVE = True
    json_data = request.json
    recv_blockcain_addr = json_data["blockchain_addr"]
    mine = Mine()
    config.STOP_MINING = False
    mine.start_mining(recv_blockcain_addr)
    return jsonify({"status": "success"}), 200


@bp.route("/mining/stop", methods=["POST"])
def mining_stop():
    """채굴 중단"""
    config.MINING_ACTIVE = False
    json_data = request.json
    stop_flag = json_data["stop_flag"]
    if stop_flag == "stop":
        print("채굴을 중단합니다. 기존 작업을 마무리 하는데 시간이 걸립니다.")
        print("system flag: config.STOP_MINING -> True")
        config.STOP_MINING = True

        # 글로벌 변수 config.STOP_MINING 상태를 체크하는 함수
        def check_stop_mining():
            while config.STOP_MINING is True:
                pass

        check_mining_stop_thread = threading.Thread(target=check_stop_mining)
        check_mining_stop_thread.daemon = True
        check_mining_stop_thread.start()
        return jsonify({"status": "stopped"}), 200

    return jsonify({"status": "fail to stop"})


@bp.route("/resolve_conflict/", methods=["GET"])
def resolve_conflicts():
    """가장 긴 블록을 찾아서 검증 -> 교체
    호출시기: 개별 노드가 채굴에 성공했을 경우
    실행순서: 채굴 성공 -> 블록생성 -> 이웃노드에게 resolve_conflict 요청
    """

    blockchain = BlockChain()

    resolve_result = blockchain.resolve_conflicts()

    return jsonify(
        {
            "status": "success" if resolve_result else "fail",
            "content": "resolve_conflict",
        }
    )


@bp.route("/is_mining_active", methods=["GET"])
def is_mining_active():
    if config.MINING_ACTIVE is True:
        return jsonify({"status": "mining_active"})

    return jsonify({"status": "mining_stop"})
