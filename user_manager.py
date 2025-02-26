from database import db, Account

def create_user(username, password, user_type):
    """
    Adds a new user to the accounts table only if the username doesn't already exist.
    Args:
        username (str): Username for the account.
        password (str): Password for the account.
        user_type (str): Role of the user ('owner' or 'worker').
    """
    # Check if the username already exists
    existing_user = Account.query.filter_by(username=username).first()
    if existing_user:
        print(f"User with username '{username}' already exists. Skipping creation.")
        return

    # Hash the password before storing it
    hashed_password = (password)

    # Add the new user
    user = Account(username=username, password=hashed_password, user_type=user_type)
    db.session.add(user)
    db.session.commit()
    print(f"User '{username}' created successfully as '{user_type}'.")


def delete_user(username):
    """
    Deletes a user from the accounts table if they exist.
    Args:
        username (str): Username of the account to delete.
    """
    user = Account.query.filter_by(username=username).first()
    if not user:
        print(f"User '{username}' not found.")
        return

    db.session.delete(user)
    db.session.commit()
    print(f"User '{username}' deleted successfully.")
