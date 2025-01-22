from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (database object)
db = SQLAlchemy()

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