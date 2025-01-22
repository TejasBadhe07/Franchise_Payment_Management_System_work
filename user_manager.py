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

    # Add the new user
    user = Account(username=username, password=password, user_type=user_type)
    db.session.add(user)
    db.session.commit()
    print(f"User '{username}' created successfully as '{user_type}'.")


# Update an existing user's information
def update_user(username, new_password=None, new_user_type=None):
    """
    Updates the details of an existing user.
    Args:
        username (str): Username to update.
        new_password (str, optional): New password (hashed).
        new_user_type (str, optional): New user type ('owner' or 'worker').
    """
    user = Account.query.filter_by(username=username).first()
    if user:
        if new_password:
            user.password = new_password
        if new_user_type:
            user.user_type = new_user_type
        db.session.commit()
        print(f'User {username} updated successfully.')
    else:
        print(f'User {username} not found.')