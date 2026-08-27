from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models import User, Wallet

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    user = User(
        full_name=data["full_name"],
        email=data["email"],
        phone=data.get("phone"),
        password_hash=generate_password_hash(data["password"]),
    )
    db.session.add(user)
    db.session.flush()  # gives user.id a real value before we commit

    wallet = Wallet(user_id=user.id, balance=0.00)
    db.session.add(wallet)

    db.session.commit()

    return jsonify({"message": "User registered", "user_id": user.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user_id": user.id}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
    })
