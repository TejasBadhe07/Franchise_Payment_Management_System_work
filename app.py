from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

app = Flask(__name__,
            template_folder='product/frontend/',  # Specify the template folder path
            static_folder='product/css'        # Specify the static folder path
            )
app.secret_key = os.urandom(24) # Important for session security

# Hardcoded user credentials (REPLACE with database interaction later)
users = {
    'owner': {'username': '111', 'password': '111'},
    'worker': {'username': 'worker', 'password': 'worker'}
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']

    if user_type in users and users[user_type]['username'] == username and users[user_type]['password'] == password:
        session['username'] = username
        session['user_type'] = user_type
        session['logged_in'] = True

        if user_type == 'owner':
            return redirect(url_for('owner_dashboard'))
        elif user_type == 'worker':
            return redirect(url_for('worker_dashboard'))
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('index'))  # Redirect to login page

@app.route('/logout')
def logout():
    session.clear() # Clears entire session
    return redirect(url_for('index'))

# Routes for owner and worker dashboards
@app.route('/owner_dashboard')
def owner_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('index'))
    return render_template('owner_dashboard.html')

@app.route('/worker_dashboard')
def worker_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('index'))
    return render_template('worker_dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)