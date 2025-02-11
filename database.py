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
    
# Define the Panel model
class Panel(db.Model):
    __tablename__ = 'panels'
    id = db.Column(db.Integer, primary_key=True)
    panel_name = db.Column(db.String(80), nullable=False, unique=True)
    points = db.Column(db.Integer, nullable=False)

    def __init__(self, panel_name, points):
        self.panel_name = panel_name
        self.points = points

    def __repr__(self):
        return f'<Panel {self.panel_name}: {self.points} points>'
    

# Define the Expense model
class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # "Sent" or "Received"

    def __init__(self, category, amount, transaction_type):
        self.category = category
        self.amount = amount
        self.transaction_type = transaction_type

    def __repr__(self):
        return f'<Expense {self.category}: {self.amount} ({self.transaction_type})>'



