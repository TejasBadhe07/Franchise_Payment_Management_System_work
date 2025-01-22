from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, Account
from user_manager import create_user, update_user

app = Flask(__name__,
            template_folder='product/frontend/',
            static_folder='product/css')
app.secret_key = 'your-secret-key'

# Configure the database URI and initialize
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database tables
with app.app_context():
    db.create_all()

    # Create sample users inside the app context
    create_user('1', '1', 'owner')
    create_user('2', '2', 'worker')

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
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

@app.route('/logout')
def logout():
    """Logs out the user and clears the session."""
    session.clear()  # Remove all session data
    flash('You have been successfully logged out.', 'info')  # Inform the user
    return redirect(url_for('login'))  # Redirect to the login page


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