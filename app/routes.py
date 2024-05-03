'''
Server routes implementation using Flask

'''

from flask import render_template, flash, redirect, url_for
from flask_login import login_user, current_user
from app import app, db
from .forms import *
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request

# Route for index.html
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Route for login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is logged in, redirect to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    # Check whether it is a valid POST request and the data verification passes
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.user_email.data).first()
        if user and check_password_hash(user.passwd_hash, form.password.data):
            # If the user exists and the password is correct
            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully as {}'.format(form.user_email.data))
            return redirect(url_for('dashboard'))  # Redirect to home page after successful login
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


# Route for register.html
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, passwd_hash=hashed_password)
    
        # Add user data to Database
        db.session.add(new_user)
        # Make sure to commit changes to the database
        db.session.commit()

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