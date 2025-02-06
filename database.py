from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuration
DATABASE_URI = 'sqlite:///payment_management.db'  # Use an appropriate URI
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)

# Define the Account model
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password, user_type):
        self.username = username
        self.password = password  # Ideally hashed
        self.user_type = user_type

    def __repr__(self):
        return f''

# Define the FinancialAccount model
class FinancialAccount(db.Model):
    __tablename__ = 'financial_accounts'
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    bank_name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __init__(self, account_name, account_number, bank_name, amount):
        self.account_name = account_name
        self.account_number = account_number
        self.bank_name = bank_name
        self.amount = amount

    def __repr__(self):
        return f''

