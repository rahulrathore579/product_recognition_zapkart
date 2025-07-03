# database.py - Database Models and Initialization

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Add more models if needed later (e.g., Order, Product)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()