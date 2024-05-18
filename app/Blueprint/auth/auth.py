from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ...models import User
from ...forms import LoginForm, RegistrationForm
from . import auth_bp
from ... import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.user_email.data).first()
        if user and check_password_hash(user.passwd_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Log in successfully as {}'.format(user.username), 'success')
            return redirect(url_for('pages.dashboard'))
        else:
            flash('Login failed: user does not exist/password is incorrect!', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/check_login', methods=['GET'])
def check_login():
    return jsonify({'is_logged_in': current_user.is_authenticated})


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, passwd_hash=hashed_password)
        new_user.set_balance(50)
        # Add user data to Database
        db.session.add(new_user)
        # Make sure to commit changes to the database
        db.session.commit()

        flash('Account created for {0}! You can now log in.'.format(form.username.data), 'success')
        return redirect(url_for('auth.login'))  # Redirect to the login page after successful registration

    return render_template('register.html', title='Register', form=form)


@auth_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('pages.index'))
