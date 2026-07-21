from extensions import db
from datetime import datetime

class TransportCard(db.Model):
    __tablename__ = "transport_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    card_number = db.Column(db.String(30), unique=True, nullable=False)
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)
