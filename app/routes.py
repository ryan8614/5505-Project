'''
Server routes implementation using Flask

'''

from flask import render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from app import app, db
from .forms import *


# Route for index.html
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Route for login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    123
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Add logic to verify the user credentials here
        flash('Logged in successfully as {}'.format(form.user_email.data))
        return redirect(url_for('home'))  # Redirect to a home or dashboard page
    return render_template('login.html', form=form)


# Route for register.html
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    456
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        
        if form.validate_on_submit():
            # Use form data to create a User Instance
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, passwd_hash=hashed_password)
        
            # Add user data to Database
            db.session.add(new_user)

        flash('Account created for {0}!'.format(form.username.data), 'success')
        return redirect(url_for('login'))  # Redirect to the login page after successful registration
    return render_template('register.html', title='Register', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/marketplace')
def marketplace():
    return render_template('index.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('index.html')