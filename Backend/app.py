from flask import Flask
from config import Config
from extensions import db, jwt
from models import User, Wallet, TransportCard, Transaction

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

with app.app_context():
    db.create_all()  # creates tables for any model that doesn't exist yet

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
