from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import wallet_service

wallet_bp = Blueprint("wallet", __name__)

@wallet_bp.route("/balance", methods=["GET"])
@jwt_required()
def balance():
    user_id = int(get_jwt_identity())
    return jsonify({"balance": wallet_service.get_balance(user_id)})

@wallet_bp.route("/topup", methods=["POST"])
@jwt_required()
def topup():
    user_id = int(get_jwt_identity())
    amount = request.get_json()["amount"]
    new_balance = wallet_service.top_up(user_id, amount)
    return jsonify({"new_balance": new_balance})

@wallet_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    txns = wallet_service.get_transaction_history(user_id)
    return jsonify([
        {
            "type": t.type,
            "amount": float(t.amount),
            "description": t.description,
            "created_at": t.created_at.isoformat(),
        }
        for t in txns
    ])
