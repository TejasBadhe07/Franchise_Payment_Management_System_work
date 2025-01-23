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


# Example usage (within a Flask route or other context)
# if __name__ == '__main__':
#     with app.app_context():
#         # Example: Add a new financial account
#         new_account = FinancialAccount(
#             account_name="My Savings",
#             account_number="1234567890",
#             bank_name="Example Bank",
#             amount=1000.50
#         )
#         db.session.add(new_account)
#         db.session.commit()

#         # Example: Query financial accounts
#         accounts = FinancialAccount.query.all()
#         for account in accounts:
#             print(f"Account Name: {account.account_name}, Balance: {account.amount}")
#     app.run(debug=True)