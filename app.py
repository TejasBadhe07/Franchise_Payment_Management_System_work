import sys
sys.stdout.reconfigure(encoding='utf-8')
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import db, Account, FinancialAccount, Panel, Expense, SubmissionHistory, BalanceHistory, AddWithdrawnPoints
from user_manager import create_user, delete_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import os
import math

from database import encrypt_database
encrypt_database()

app = Flask(__name__,
            template_folder='product/frontend/',
            static_folder='product/css')
app.secret_key = 'your-secret-key'

# ✅ Ensure the database directory exists
DB_DIR = os.path.abspath("data")  # Convert to absolute path
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
    print(f" Created database directory: {DB_DIR}")

# ✅ Store SQLite database inside the "data" folder
DB_PATH = os.path.join(DB_DIR, "payment_management.db")
print(f" Database Path: {DB_PATH}")  # Debugging output

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# # Configure the database URI and initialize
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment_management.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# Routes
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    print(f"User name is -----------------------------{username}")
    password = request.form['password']
    user_type = request.form['user_type']

    user = Account.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password) and user.user_type == user_type:
        session['username'] = username
        session['user_type'] = user_type
        session['logged_in'] = True

        if user_type == 'owner':
            return redirect(url_for('owner_dashboard'))
        elif user_type == 'worker':
            return redirect(url_for('worker_dashboard'))
    else:
        flash('Invalid username, password, or user type.', 'error')
        return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the entire session
    session.clear()
    
    # Return a success response to the JavaScript fetch call
    return {"message": "Logout successful"}, 200

########################################################## OWNER DASHBOARD ##########################################################

@app.route('/owner_dashboard')
def owner_dashboard():
    if not session.get('logged_in') or session.get('user_type') != 'owner':
        flash('Access denied. Please log in as owner.', 'error')
        return redirect(url_for('index'))

    # Fetch recent submissions with Profit/Loss and Plus/Minus
    recent_submissions = BalanceHistory.query.order_by(BalanceHistory.timestamp.desc()).limit(10).all()

    logged_in_user = session.get('username')

    # Fetch all users but allow deletion only for others (not the logged-in owner)
    users = Account.query.all()

    return render_template('owner_dashboard.html', recent_submissions=recent_submissions, 
                           users=users, logged_in_user=logged_in_user)

@app.route('/create_user', methods=['POST'])
def create_user_route():
    if not session.get('logged_in') or session.get('user_type') != 'owner':
        flash('Access denied. Only owners can create users.', 'error')
        return redirect(url_for('owner_dashboard'))

    username = request.form.get('username')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    if not username or not password or not user_type:
        flash('All fields are required.', 'error')
        return redirect(url_for('owner_dashboard'))

    # Call the function from user_manager.py
    create_user(username, password, user_type)

    flash(f'User {username} created successfully!', 'success')
    return redirect(url_for('owner_dashboard'))

@app.route('/delete_user', methods=['POST'])
def delete_user_route():
    if not session.get('logged_in') or session.get('user_type') != 'owner':
        flash('Access denied. Only owners can delete users.', 'error')
        return redirect(url_for('owner_dashboard'))

    username = request.form.get('username')

    if not username:
        flash('Please select a user to delete.', 'error')
        return redirect(url_for('owner_dashboard'))

    # Call the function to delete user
    delete_user(username)

    flash(f'User "{username}" deleted successfully!', 'success')
    return redirect(url_for('owner_dashboard'))

@app.route('/blueprint', methods=['POST'])
def blueprint():
    if not session.get('logged_in') or session.get('user_type') != 'owner':
        flash('Access denied. Please log in as owner.', 'error')
        return redirect(url_for('index'))

    submission_date = request.form.get('submission_date')

    if not submission_date:
        flash('Please select a date.', 'error')
        return redirect(url_for('owner_dashboard'))
    print(f"Submission date is {submission_date}")

    # Fetch records filtered by selected date
    account_records = SubmissionHistory.query.filter(SubmissionHistory.record_type == 'Account').filter(
        db.func.strftime('%Y-%m-%d', SubmissionHistory.timestamp) == submission_date).all()

    panel_records = SubmissionHistory.query.filter(SubmissionHistory.record_type == 'Panel').filter(
        db.func.strftime('%Y-%m-%d', SubmissionHistory.timestamp) == submission_date).all()

    expense_records = SubmissionHistory.query.filter(SubmissionHistory.record_type == 'Expense').filter(
        db.func.strftime('%Y-%m-%d', SubmissionHistory.timestamp) == submission_date).all()

    # Calculate Summary
    old_balance = sum(record.amount_or_points for record in account_records if record.record_name == 'Old Balance')
    new_balance = sum(record.amount_or_points for record in account_records if record.record_name == 'New Balance')
    profit_loss = sum(record.amount_or_points for record in account_records if record.record_name == 'Profit/Loss')
    plus_minus = sum(record.amount_or_points for record in account_records if record.record_name == 'Plus/Minus')

    return render_template(
        'owner_dashboard.html',
        account_records=account_records,
        panel_records=panel_records,
        expense_records=expense_records,
        old_balance=old_balance,
        new_balance=new_balance,
        profit_loss=profit_loss,
        plus_minus=plus_minus
    )




########################################################## WORKER DASHBOARD ##########################################################


@app.route('/worker_dashboard')
def worker_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))

    username = session.get('username')
    accounts = FinancialAccount.query.all()
    panels = Panel.query.all()
    expenses = Expense.query.all()

    total_panel_points = db.session.query(db.func.sum(Panel.points)).scalar() or 0
    total_account_balance = db.session.query(db.func.sum(FinancialAccount.amount)).scalar() or 0
    total_sent = db.session.query(db.func.sum(Expense.amount)).filter_by(transaction_type='Sent').scalar() or 0
    total_received = db.session.query(db.func.sum(Expense.amount)).filter_by(transaction_type='Received').scalar() or 0

    # ✅ Fetch latest submission from BalanceHistory
    last_submission = BalanceHistory.query.filter_by(username=username).order_by(BalanceHistory.timestamp.desc()).first()
    
    old_balance = last_submission.old_balance if last_submission else 0  
    old_points = last_submission.old_points if last_submission else 0    
    plus_minus = last_submission.plus_or_minus if last_submission else 0  
    profit_loss = last_submission.profit_or_loss if last_submission else 0  

    # ✅ Correct New Balance Calculation
    new_balance = total_account_balance + total_sent

    return render_template(
        'worker_dashboard.html',
        accounts=accounts,
        panels=panels,
        expenses=expenses,
        total_panel_points=total_panel_points,
        total_account_balance=total_account_balance,
        total_sent=total_sent,
        total_received=total_received,
        new_balance=new_balance,
        old_balance=old_balance,  
        old_points=old_points,    
        plus_minus=plus_minus,  # ✅ Fetching from BalanceHistory
        profit_loss=profit_loss  # ✅ Fetching from BalanceHistory
    )

def calculate_balance_metrics(total_account_balance, total_panel_points, total_sent, total_received,
                             old_balance, old_points, total_points_added, total_points_withdrawn):
    """
    Calculate balance metrics including new_balance, new_points, plus_minus, and profit_loss.
    
    Args:
        total_account_balance (float): Current total account balance
        total_panel_points (float): Current total panel points
        total_sent (float): Total amount sent
        total_received (float): Total amount received
        old_balance (float): Previous account balance
        old_points (float): Previous panel points
        total_points_added (float): Total points added
        total_points_withdrawn (float): Total points withdrawn
        
    Returns:
        tuple: (new_balance, new_points, plus_minus, profit_loss)
    """
    print("=== Input Parameters ===")
    print(f"total_account_balance: {total_account_balance}")
    print(f"total_panel_points: {total_panel_points}")
    print(f"total_sent: {total_sent}")
    print(f"total_received: {total_received}")
    print(f"old_balance: {old_balance}")
    print(f"old_points: {old_points}")
    print(f"total_points_added: {total_points_added}")
    print(f"total_points_withdrawn: {total_points_withdrawn}")
    print("")
    
    # Calculate new values
    new_balance = total_account_balance + total_sent
    new_points = total_panel_points

    old_points = old_points + total_points_added - total_points_withdrawn
    print(f"Old points is {old_points}")
    
    print("=== Calculated New Values ===")
    print(f"new_balance = {total_account_balance} + {total_sent} = {new_balance}")
    print(f"new_points = {new_points}")
    print("")
    
    # Calculate profit/loss
    profit_loss = old_points - new_points
    
    print("=== Profit/Loss Calculation ===")
    print(f"profit_loss = {old_points} - {new_points} = {profit_loss}")
    print(f"{'Profit' if profit_loss > 0 else 'Loss'} detected")
    print("")
    
    # Calculate differences
    points_difference = old_points - new_points
    balance_difference = new_balance - old_balance
    
    print("=== Differences ===")
    print(f"points_difference = {old_points} - {new_points} = {points_difference}")
    print(f"balance_difference = {new_balance} - {old_balance} = {balance_difference}")
    print("")
    
    # Calculate difference based on profit or loss
    if profit_loss > 0:  # It's a profit
        difference = balance_difference - points_difference
        print("=== Profit Case ===")
        print(f"difference = {balance_difference} - {points_difference} = {difference}")
    else:  # It's a loss
        # Ensure points_difference is positive for loss case
        abs_points_difference = abs(points_difference)
        difference = balance_difference + abs_points_difference
        print("=== Loss Case ===")
        print(f"points_difference (absolute value): {abs_points_difference}")
        print(f"difference = {balance_difference} + {abs_points_difference} = {difference}")
    print("")
    
    # Calculate plus_minus
    plus_minus = difference - total_received
    
    print("=== Plus Minus Calculation ===")
    print(f"plus_minus = {difference} - {total_received} = {plus_minus}")
    print("")
    
    print("=== Final Results ===")
    print(f"new_balance: {new_balance}")
    print(f"new_points: {new_points}")
    print(f"plus_minus: {plus_minus}")
    print(f"profit_loss: {profit_loss}")
    print("")
    
    return new_balance, new_points, plus_minus, profit_loss

############################################# SUBMISSION MANAGEMENT ############################################# 

SUBMISSION_LIMIT = 0
@app.route('/submit_data', methods=['POST'])
def submit_data():
    if not session.get('logged_in'):
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    username = session.get('username')
    timestamp = datetime.now()

    if SUBMISSION_LIMIT == 1:
        last_24_hours = timestamp - timedelta(hours=24)
        submission_count = SubmissionHistory.query.filter(
            SubmissionHistory.username == username,
            SubmissionHistory.timestamp >= last_24_hours
        ).count()
        if submission_count >= 2:
            return jsonify({'status': 'error', 'message': 'Submission limit reached. You can only submit twice in 24 hours.'}), 403

    # ✅ Fetch financial data
    total_panel_points = db.session.query(db.func.sum(Panel.points)).scalar() or 0
    total_account_balance = db.session.query(db.func.sum(FinancialAccount.amount)).scalar() or 0
    total_sent = db.session.query(db.func.sum(Expense.amount)).filter_by(transaction_type='Sent').scalar() or 0
    total_received = db.session.query(db.func.sum(Expense.amount)).filter_by(transaction_type='Received').scalar() or 0
    total_points_added = db.session.query(db.func.sum(AddWithdrawnPoints.points)).filter_by(transaction_type="Added").scalar() or 0
    total_points_withdrawn = db.session.query(db.func.sum(AddWithdrawnPoints.points)).filter_by(transaction_type="Withdrawn").scalar() or 0

    # ✅ Fetch previous submission data from BalanceHistory
    last_submission = BalanceHistory.query.filter_by(username=username).order_by(BalanceHistory.timestamp.desc()).first()
    old_balance = last_submission.total_account_balance if last_submission else 0
    old_points = last_submission.new_points if last_submission else 0

    # ✅ Calculate financial metrics using updated function
    new_balance, new_points, plus_minus, profit_loss = calculate_balance_metrics(
        total_account_balance, total_panel_points, total_sent, total_received,
        old_balance, old_points, total_points_added, total_points_withdrawn)

    try:
        # ✅ Save records to SubmissionHistory
        submission_records = []
        financial_accounts = FinancialAccount.query.all()
        for account in financial_accounts:
            submission_records.append(SubmissionHistory(username=username, timestamp=timestamp, record_type="Account",
                                                        record_name=account.account_name, amount_or_points=account.amount))

        panels = Panel.query.all()
        for panel in panels:
            submission_records.append(SubmissionHistory(username=username, timestamp=timestamp, record_type="Panel",
                                                        record_name=panel.panel_name, amount_or_points=panel.points))

        expenses = Expense.query.all()
        for expense in expenses:
            submission_records.append(SubmissionHistory(username=username, timestamp=timestamp, record_type="Expense",
                                                        record_name=expense.category, amount_or_points=expense.amount,
                                                        transaction_type=expense.transaction_type))

        add_withdrawn_entries = AddWithdrawnPoints.query.all()
        for entry in add_withdrawn_entries:
            submission_records.append(SubmissionHistory(
                username=username,
                timestamp=timestamp,
                record_type="Panel",
                transaction_type=entry.transaction_type,
                record_name=entry.panel_name,
                amount_or_points=entry.points
            ))
        db.session.bulk_save_objects(submission_records)
        db.session.query(AddWithdrawnPoints).delete()

        # ✅ Save new BalanceHistory record
        balance_entry = BalanceHistory(
            username=username,
            timestamp=timestamp,
            total_account_balance=total_account_balance,
            old_balance=old_balance,
            new_balance=new_balance,
            old_points=old_points,
            new_points=new_points,
            plus_or_minus=plus_minus,
            profit_or_loss=profit_loss
        )
        db.session.add(balance_entry)
        db.session.commit()

        # ✅ Reset financial data
        for account in financial_accounts:
            account.amount = 0
        for panel in panels:
            panel.points = 0
        db.session.query(Expense).delete()
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Data submitted successfully!', 'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_account_balance': total_account_balance, 'total_panel_points': total_panel_points,
                        'total_sent': total_sent, 'total_received': total_received, 'new_balance': new_balance,
                        'new_points': new_points, 'plus_minus': plus_minus, 'profit_loss': profit_loss}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Submission failed! Error: {str(e)}'}), 500


@app.after_request
def add_header(response):
    # Prevent caching of responses
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

############################################# PAYMENT MANAGEMENT #############################################


@app.route('/add_accounts', methods=['POST'])
def add_account():
    # Print incoming form data to the console for debugging
    print("add_account route accessed")
    
    # Get the form data
    account_name = request.form.get('account_name')
    account_number = request.form.get('account_number')
    bank_name = request.form.get('bank_name')
    balance = request.form.get('balance')

    # Print the form data to the console for debugging
    print(f"Account Name: {account_name}")
    print(f"Account Number: {account_number}")
    print(f"Bank Name: {bank_name}")
    print(f"Balance: {balance}")
    
    # Check if all fields are provided
    if not (account_name and account_number and bank_name and balance):
        flash("All fields are required!", "error")
        return redirect(url_for('worker_dashboard'))

    # Insert the data into the database
    try:
        new_account = FinancialAccount(
            account_name=account_name,
            account_number=account_number,
            bank_name=bank_name,
            amount=balance  # Store the balance as 'amount'
        )
        db.session.add(new_account)
        db.session.commit()  # Commit the transaction

        flash("Account added successfully!", "success")
        return redirect(url_for('worker_dashboard'))
    except Exception as e:
        # If any error occurs, print it to the console
        print(f"Error inserting account into database: {e}")
        flash("There was an error adding the account. Please try again.", "error")
        return redirect(url_for('worker_dashboard'))

@app.route('/delete_account/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    try:
        # Find the account by ID and delete it
        account_to_delete = FinancialAccount.query.get(account_id)
        if account_to_delete:
            db.session.delete(account_to_delete)  # Delete the account
            db.session.commit()  # Commit the transaction
            flash("Account deleted successfully!", "success")
            return {"message": "Account deleted successfully!"}, 200
        else:
            flash("Account not found.", "error")
            return {"message": "Account not found."}, 404
    except Exception as e:
        print(f"Error deleting account: {e}")
        flash("There was an error deleting the account.", "error")
        return {"message": "Error deleting account."}, 500


# Route to Update Balance
@app.route('/update_balance/<int:account_id>', methods=['POST'])
def update_balance(account_id):
    data = request.json
    amount = data.get('amount')
    date = data.get('date')

    # Validate inputs
    if not amount or not date:
        return jsonify({'error': 'Invalid data'}), 400

    # Find the account and update balance
    account = FinancialAccount.query.get(account_id)
    if account:
        account.amount = float(amount)  # Just Replace the Old Value
        db.session.commit()
        return jsonify({'message': 'Balance updated successfully!'}), 200
    else:
        return jsonify({'error': 'Account not found'}), 404


# Route to Update Panel Points
@app.route('/update_points/<string:panel_name>', methods=['POST'])
def update_points(panel_name):
    data = request.json
    points = data.get('points')
    date = data.get('date')

    # Validate input
    if not points or not date:
        return jsonify({'error': 'Invalid data'}), 400

    # Find the panel and update points
    panel = Panel.query.filter_by(panel_name=panel_name).first()
    if panel:
        panel.points = float(points)  # Direct Replace
        db.session.commit()
        return jsonify({'message': 'Points updated successfully!'}), 200
    else:
        return jsonify({'error': 'Panel not found'}), 404


    
####################################### Tasks ########################################

# Add Panel to Database
@app.route('/add_panel', methods=['POST'])
def add_panel():
    panel_name = request.form.get('panel_name')
    panel_points = request.form.get('panel_points')

    if not panel_name or not panel_points:
        return jsonify({'status': 'error', 'message': 'Panel name and points are required.'}), 400

    try:
        # Create new panel entry
        new_panel = Panel(panel_name=panel_name, points=int(panel_points))
        db.session.add(new_panel)
        db.session.commit()  # Save changes to DB

        print(f"Added Panel Name: {panel_name}, Points: {panel_points}")
        return jsonify({'status': 'success', 'message': 'Panel added successfully!'})
    except Exception as e:
        print(f"Error adding panel: {e}")
        db.session.rollback()  # Rollback in case of error
        return jsonify({'status': 'error', 'message': 'Error adding panel. Try again!'}), 500


# Delete Panel from Database
@app.route('/delete_panel/<int:panel_id>', methods=['POST'])
def delete_panel(panel_id):
    try:
        # Find the panel by ID and delete it
        panel_to_delete = Panel.query.get(panel_id)
        if panel_to_delete:
            db.session.delete(panel_to_delete)
            db.session.commit()
            flash("Panel deleted successfully!", "success")
            return {"message": "Panel deleted successfully!"}, 200
        else:
            flash("Panel not found.", "error")
            return {"message": "Panel not found."}, 404
    except Exception as e:
        print(f"Error deleting panel: {e}")
        flash("There was an error deleting the panel.", "error")
        return {"message": "Error deleting panel."}, 500

    
####################################### Expenses ########################################

@app.route('/add_expense', methods=['POST'])
def add_expense():
    category = request.form.get('expense_category')
    amount = request.form.get('expense_amount')
    transaction_type = request.form.get('transaction_type')  # "Sent" or "Received"

    if not category or not amount or not transaction_type:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    try:
        new_expense = Expense(category=category, amount=float(amount), transaction_type=transaction_type)
        db.session.add(new_expense)
        db.session.commit()

        print(f"Added Expense: {category}, Amount: {amount}, Type: {transaction_type}")
        return jsonify({'status': 'success', 'message': 'Expense added successfully!'})
    except Exception as e:
        print(f"Error adding expense: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error adding expense. Try again!'}), 500

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    try:
        # Find the expense by ID and delete it
        expense_to_delete = Expense.query.get(expense_id)
        if expense_to_delete:
            db.session.delete(expense_to_delete)
            db.session.commit()
            flash("Expense deleted successfully!", "success")
            return {"message": "Expense deleted successfully!"}, 200
        else:
            flash("Expense not found.", "error")
            return {"message": "Expense not found."}, 404
    except Exception as e:
        print(f"Error deleting expense: {e}")
        flash("There was an error deleting the expense.", "error")
        return {"message": "Error deleting expense."}, 500
    

@app.route('/add_points/<string:panel_name>', methods=['POST'])
def add_points(panel_name):
    username = session.get('username')
    data = request.get_json()
    points = data.get('points', 0)

    if points <= 0:
        return jsonify({"error": "Invalid points"}), 400

    entry = AddWithdrawnPoints(
    username=username,
    panel_name=panel_name,  # 🔥 Save panel name here
    transaction_type="Added",
    points=points,
    timestamp=datetime.utcnow())

    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": f"{points} Points Added to {panel_name} by {username} ✅"}), 200


@app.route('/withdraw_points/<string:panel_name>', methods=['POST'])
def withdraw_points(panel_name):
    username = session.get('username')
    data = request.get_json()
    points = data.get('points', 0)

    if points <= 0:
        return jsonify({"error": "Invalid points"}), 400

    entry = AddWithdrawnPoints(
    username=username,
    panel_name=panel_name,  # 🔥 Save panel name here
    transaction_type="Withdrawn",
    points=points,
    timestamp=datetime.utcnow())

    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": f"{points} Points Withdrawn from {panel_name} by {username} ❌"}), 200


@app.route('/calculate_plus_minus/<string:panel_name>', methods=['GET'])
def calculate_plus_minus(panel_name):
    # Get total added points
    total_added = db.session.query(db.func.sum(SubmissionHistory.amount_or_points)).filter_by(
        record_type="Panel", transaction_type="Added", record_name=panel_name
    ).scalar() or 0

    # Get total withdrawn points
    total_withdrawn = db.session.query(db.func.sum(SubmissionHistory.amount_or_points)).filter_by(
        record_type="Panel", transaction_type="Withdrawn", record_name=panel_name
    ).scalar() or 0

    plus_minus = total_added - total_withdrawn

    return jsonify({
        "panel": panel_name,
        "total_added": total_added,
        "total_withdrawn": total_withdrawn,
        "plus_minus": plus_minus
    }), 200


####################################### Submission ########################################

# Route to get the last submission time
@app.route('/get_last_submission_time', methods=['GET'])
def get_last_submission_time():
    username = session.get('username')
    last_submission = SubmissionHistory.query.filter_by(username=username).order_by(SubmissionHistory.timestamp.desc()).first()

    if last_submission:
        return jsonify({'timestamp': last_submission.timestamp.strftime('%Y-%m-%d %H:%M:%S')})
    else:
        return jsonify({'timestamp': None})


# Initialize database tables
with app.app_context():
    db.create_all()

    # Create sample users inside the app context
    create_user('LM0010','LM0010','owner')
    create_user('User','User#0010','worker')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)