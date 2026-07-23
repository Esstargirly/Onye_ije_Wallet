from flask import Flask
from config import Config
from extensions import db, jwt
from models import User, Wallet, TransportCard, Transaction
from routes.auth import auth_bp
from routes.wallet import wallet_bp
from routes.cards import cards_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")  # add this
app.register_blueprint(wallet_bp, url_prefix="/api/wallet")
app.register_blueprint(cards_bp, url_prefix="/api/cards")

with app.app_context():
    db.create_all()  # creates tables for any model that doesn't exist yet

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
