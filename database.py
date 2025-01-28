from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuration
DATABASE_URI = 'sqlite:///your_database.db'  # Use an appropriate URI
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)

# Define the Account model for user authentication
class Account(db.Model):
    __tablename__ = 'accounts'  # Table name in the database

    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username
    password = db.Column(db.String(120), nullable=False)  # Password (hashed)
    user_type = db.Column(db.String(20), nullable=False)  # 'owner' or 'worker'

    def __init__(self, username, password, user_type):
        self.username = username
        self.password = password  # Ideally hashed
        self.user_type = user_type

    def __repr__(self):
        return f'<Account {self.username}>'

# Define the FinancialAccount model
class FinancialAccount(db.Model):
    __tablename__ = 'financial_accounts'  # Table name in the database

    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    account_name = db.Column(db.String(80), nullable=False)  # Account name
    account_number = db.Column(db.String(20), nullable=False)  # Account number
    bank_name = db.Column(db.String(80), nullable=False)  # Bank name
    amount = db.Column(db.Float, nullable=False)  # Account balance

    def __init__(self, account_name, account_number, bank_name, amount):
        self.account_name = account_name
        self.account_number = account_number
        self.bank_name = bank_name
        self.amount = amount

    def __repr__(self):
        return f'<FinancialAccount {self.account_name}>'
    
class Panel(db.Model):
    __tablename__ = 'panels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, nullable=False)

    def __init__(self, name, points):
        self.name = name
        self.points = points

    def __repr__(self):
        return f'<Panel {self.name}>'