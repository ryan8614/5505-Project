from flask import Blueprint

# Create a Blueprint for basic page access
pages_bp = Blueprint('pages', __name__, template_folder='../../templates', static_folder='../../static')

# Import all view functions from pages.py in the current directory
from .pages import dashboard, marketplace, privacy, terms, about