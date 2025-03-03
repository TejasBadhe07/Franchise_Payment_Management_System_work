import sys
sys.stdout.reconfigure(encoding='utf-8')
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


# Configuration
import sqlite3

DATABASE_PASSWORD = "Tejas@07"  # 🔑 Your Secret Password

DATABASE_URI = f"sqlite:///data/payment_management.db"

def encrypt_database():
    conn = sqlite3.connect("data/payment_management.db")
    conn.execute(f"PRAGMA key = '{DATABASE_PASSWORD}';")  # Encrypt DB
    print("🔒 Database Encrypted with Password")
    conn.close()

encrypt_database()
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
    points = db.Column(db.Float, nullable=False)

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

# Define the SubmissionHistory model
class SubmissionHistory(db.Model):
    __tablename__ = 'submission_history'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    record_type = db.Column(db.String(20), nullable=False)  # "Account", "Panel", "Expense"
    record_name = db.Column(db.String(80), nullable=False)
    amount_or_points = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=True)  # "NULL", "Sent", "Received"

    def __repr__(self):
        return f'<Submission {self.username} - {self.record_name}: {self.amount_or_points} ({self.transaction_type})>'
    
class BalanceHistory(db.Model):
    __tablename__ = 'balance_history'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    total_account_balance = db.Column(db.Float, nullable=False)
    old_balance = db.Column(db.Float, nullable=True)
    new_balance = db.Column(db.Float, nullable=True)
    old_points = db.Column(db.Float, nullable=True)
    new_points = db.Column(db.Float, nullable=True)
    profit_or_loss = db.Column(db.Float, nullable=True)
    plus_or_minus = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<BalanceHistory {self.username} - New Balance: {self.new_balance}, Profit/Loss: {self.profit_or_loss}>'
    
class AddWithdrawnPoints(db.Model):
    __tablename__ = 'add_withdrawn_points'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    panel_name = db.Column(db.String(80), nullable=False)  # 🔥 Add this column
    timestamp = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Float, nullable=False)  # Positive + Negative
    transaction_type = db.Column(db.String(10), nullable=False)  # "Added" or "Withdrawn"

    def __repr__(self):
        return f'<{self.username} - {self.points} ({self.transaction_type})>'
