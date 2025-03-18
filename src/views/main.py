from flask import Blueprint, jsonify

bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def home():
    return "hello world"


@bp.route("/get-chain", methods=["GET"])
def get_chain():
    return "get_chain"
