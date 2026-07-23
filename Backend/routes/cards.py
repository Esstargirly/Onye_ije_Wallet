from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import TransportCard

cards_bp = Blueprint("cards", __name__)

@cards_bp.route("/link", methods=["POST"])
@jwt_required()
def link_card():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    card_number = data["card_number"]

    if TransportCard.query.filter_by(card_number=card_number).first():
        return jsonify({"error": "Card already linked to another account"}), 400

    card = TransportCard(user_id=user_id, card_number=card_number)
    db.session.add(card)
    db.session.commit()
    return jsonify({"message": "Card linked successfully"}), 201
