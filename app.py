from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, Account, FinancialAccount
from user_manager import create_user, update_user

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

    return render_template('worker_dashboard.html', accounts=accounts)  # Pass accounts to the template

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


from flask import Flask, request, jsonify
from database import db, FinancialAccount
from datetime import datetime

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
    
####################################### Tasks ########################################

# Mock data (for simplicity)
panels = []
expenses = []

@app.route('/add_panel', methods=['POST'])
def add_panel():
    # Get the form data from the request
    panel_name = request.form.get('panel_name')
    panel_points = request.form.get('panel_points')

    if not panel_name or not panel_points:
        return jsonify({'status': 'error', 'message': 'Panel name and points are required.'}), 400

    # Add to the panels list (or database in real app)
    panels.append({'name': panel_name, 'points': panel_points})
    
    return jsonify({'status': 'success', 'message': 'Panel added successfully!'})

@app.route('/delete_panel', methods=['POST'])
def delete_panel():
    panel_name = request.form.get('panel_name')

    if not panel_name:
        return jsonify({'status': 'error', 'message': 'Panel name is required.'}), 400

    # Find and remove the panel
    global panels
    panels = [panel for panel in panels if panel['name'] != panel_name]
    
    return jsonify({'status': 'success', 'message': 'Panel deleted successfully!'})

@app.route('/add_expense', methods=['POST'])
def add_expense():
    expense_name = request.form.get('expense_name')
    expense_amount = request.form.get('expense_amount')

    if not expense_name or not expense_amount:
        return jsonify({'status': 'error', 'message': 'Expense name and amount are required.'}), 400

    # Add to the expenses list (or database in real app)
    expenses.append({'name': expense_name, 'amount': expense_amount})

    return jsonify({'status': 'success', 'message': 'Expense added successfully!'})

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    expense_name = request.form.get('expense_name')
    print(expense_name)

    if not expense_name:
        return jsonify({'status': 'error', 'message': 'Expense name is required.'}), 400

    # Find and remove the expense
    global expenses
    expenses = [expense for expense in expenses if expense['name'] != expense_name]

    return jsonify({'status': 'success', 'message': 'Expense deleted successfully!'})


# Initialize database tables
with app.app_context():
    db.create_all()

    # Create sample users inside the app context
    # create_user('owner1', 'password123', 'owner')
    # create_user('worker1', 'password456', 'worker')

    #create_user('1','1','owner')
    #create_user('2','2','worker')


if __name__ == '__main__':
    app.run(debug=True)