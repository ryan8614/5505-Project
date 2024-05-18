from flask import Blueprint

# Create a Blueprint for trade
trade_bp = Blueprint('trade', __name__, template_folder='../../templates')

# Import all view functions from trade.py in the current directory
from .trade import trade, update_trade_price, redeem, search_fragments, get_fragments, buy