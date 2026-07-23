from extensions import db
from models import Wallet, Transaction

def get_balance(user_id):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        raise ValueError("Wallet not found for this user")
    return float(wallet.balance)

def top_up(user_id, amount):
    if amount <= 0:
        raise ValueError("Top-up amount must be positive")

    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        raise ValueError("Wallet not found for this user")

    wallet.balance = float(wallet.balance) + amount
    db.session.add(Transaction(
        wallet_id=wallet.id,
        type="top_up",
        amount=amount,
        description="Wallet top-up"
    ))
    db.session.commit()
    return float(wallet.balance)

def get_transaction_history(user_id, limit=20):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        raise ValueError("Wallet not found for this user")
    return (
        Transaction.query
        .filter_by(wallet_id=wallet.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
