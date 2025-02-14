from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import db, Account, FinancialAccount, Panel, Expense
from user_manager import create_user
from datetime import datetime

app = Flask(__name__,
            template_folder='product/frontend/',
            static_folder='product/css')
app.secret_key = 'your-secret-key'

# Configure the database URI and initialize
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    print(f"User name is -----------------------------{username}")
    password = request.form['password']
    user_type = request.form['user_type']

    user = Account.query.filter_by(username=username, password=password).first()

    if user and user.user_type == user_type:
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



@app.route('/owner_dashboard')
def owner_dashboard():
    if not session.get('logged_in'):  # Check if the user is logged in
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))
    return render_template('owner_dashboard.html')

@app.route('/worker_dashboard')
def worker_dashboard():
    if not session.get('logged_in'):  # Check if the user is logged in
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))

    # Fetch all financial accounts from the database
    accounts = FinancialAccount.query.all()  # Query all records from the table

    # Fetch all panels from the database
    panels = Panel.query.all()

    # # Fetch all expenses from the database
    expenses = Expense.query.all()

    total_panel_points = db.session.query(db.func.sum(Panel.points)).scalar() or 0
    total_account_balance = db.session.query(db.func.sum(FinancialAccount.amount)).scalar() or 0
    total_sent = db.session.query(db.func.sum(Expense.amount)).filter_by(transaction_type='Sent').scalar() or 0
    total_received = db.session.query(db.func.sum(Expense.amount)).filter_by(transaction_type='Received').scalar() or 0

    return render_template('worker_dashboard.html', accounts=accounts, panels=panels, expenses=expenses,
                           total_panel_points=total_panel_points,
                           total_account_balance=total_account_balance,
                           total_sent=total_sent, total_received=total_received, 
                           new_balance = total_sent + total_account_balance - total_received)

                           
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




# Route to update balance
@app.route('/update_balance/<int:account_id>', methods=['POST'])
def update_balance(account_id):
    data = request.json
    amount = data.get('amount')
    date = data.get('date')

    # Validate inputs
    if not amount or not date:
        return jsonify({'error': 'Invalid data'}), 400

    # Find the account and update the balance
    account = FinancialAccount.query.get(account_id)
    if account:
        account.amount += float(amount)  # Add the amount to the current balance
        db.session.commit()
        return jsonify({'message': 'Balance updated successfully!'}), 200
    else:
        return jsonify({'error': 'Account not found'}), 404
    
# Route to update panel points
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
        panel.points += float(points)  # Add the new points
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
    
# Route to add points to a panel
@app.route('/add_points/<string:panel_name>', methods=['POST'])
def add_points(panel_name):
    data = request.json
    points = data.get('points')

    # Ensure points is a valid number
    try:
        points = float(points)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid points value. Must be a number.'}), 400

    if points <= 0:
        return jsonify({'error': 'Points must be greater than zero'}), 400

    panel = Panel.query.filter_by(panel_name=panel_name).first()
    if panel:
        panel.points += points  # Increase panel points
        db.session.commit()
        return jsonify({'message': 'Points added successfully!'}), 200
    else:
        return jsonify({'error': 'Panel not found'}), 404


# Route to withdraw points from a panel
@app.route('/withdraw_points/<string:panel_name>', methods=['POST'])
def withdraw_points(panel_name):
    data = request.json
    points = data.get('points')

    # Ensure points is a valid number
    try:
        points = float(points)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid points value. Must be a number.'}), 400

    if points <= 0:
        return jsonify({'error': 'Points must be greater than zero'}), 400

    panel = Panel.query.filter_by(panel_name=panel_name).first()
    if panel:
        if panel.points >= points:
            panel.points -= points  # Deduct points
            db.session.commit()
            return jsonify({'message': 'Points withdrawn successfully!'}), 200
        else:
            return jsonify({'error': 'Not enough points available to withdraw'}), 400
    else:
        return jsonify({'error': 'Panel not found'}), 404

# Initialize database tables
with app.app_context():
    db.create_all()

    # Create sample users inside the app context
    create_user('1','1','owner')
    create_user('2','2','worker')


if __name__ == '__main__':
    app.run(debug=True)