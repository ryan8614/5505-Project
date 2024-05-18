from flask import Blueprint

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__, template_folder='../../templates')

# Import all view functions from auth.py in the current directory
from .auth import login, check_login, register, logout

