from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.gemma_assistant import ask_gemma

assistant_bp = Blueprint("assistant", __name__)

@assistant_bp.route("", methods=["POST"])
@jwt_required()
def assistant():
    user_id = int(get_jwt_identity())
    message = request.get_json()["message"]
    reply = ask_gemma(message, user_id=user_id)
    return jsonify({"reply": reply})