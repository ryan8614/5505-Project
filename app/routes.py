'''
Server routes implementation using Flask

'''

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from .forms import LoginForm, RegistrationForm
from .models import User
from . import db, app, processor



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
            flash('Log in successfully as {}'.format(form.user_email.data), 'success')
            # Redirect to home page after successful login
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed: user does not exist/password is incorrect!', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


# Route for register.html
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, passwd_hash=hashed_password, balance=500)
    
        # Add user data to Database
        db.session.add(new_user)
        # Make sure to commit changes to the database
        db.session.commit()

        flash('Account created for {0}!'.format(form.username.data), 'success')
        return redirect(url_for('login'))  # Redirect to the login page after successful registration

    return render_template('register.html', title='Register', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/marketplace')
def marketplace():
    return render_template('index.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        num_parts = request.form.get('num_parts', type=int)
        
        if file and file.filename and processor.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(processor.upload_folder, filename)

            # Check if the file already exists
            if os.path.exists(file_path):
                flash('A file with this name already exists. Please upload a file with a different name or delete the existing one.')
                return redirect(request.url)

            save_result = processor.save_file(file)
            if save_result:
                processor.split_image(file_path, num_parts)
                flash('File has been uploaded and processed successfully.')
                return redirect(url_for('upload'))
            else:
                flash('File format not supported.')
                return redirect(request.url)
            
        else:
            flash('Invalid file or file format not supported.')
            return redirect(url_for('upload'))
        
    else:
        return render_template('upload.html')


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))
    else:
        flash('No active session found - you were not logged in.', 'danger')
        return redirect(url_for('index'))
