from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, SubmitField, PasswordField, ValidationError, HiddenField, DecimalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from .models import User


class LoginForm(FlaskForm):
    """
    Form for users to login.

    This form represents a simple login interface with email and password fields.
    It uses validators to ensure that both fields are appropriately filled out.
    """
    user_email = StringField('Email', validators=[DataRequired(), Email(message='Invalid email address')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=6, message='Password must be at least 6 characters long')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already in use. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email address is already registered. Please use a different email address.')
        

class BuyForm(FlaskForm):
    fragment_id = StringField('FragmentId', validators=[DataRequired()])
    buyer = StringField('Buyer', validators=[DataRequired()])
    submit = SubmitField('Confirm')