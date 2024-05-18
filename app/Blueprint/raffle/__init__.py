from flask import Blueprint
from ...ImageProcessor import ImageProcessor
import os

# Create a Blueprint for raffle
raffle_bp = Blueprint('raffle', __name__, template_folder='../../templates')

# Create the required directories
os.makedirs('static/uploads/raffle', exist_ok=True)
os.makedirs('static/outputs/raffle', exist_ok=True)

# Initialize image processor
processor = ImageProcessor('static/uploads/raffle', 'static/outputs/raffle')

# Import all view functions from raffle.py in the current directory
from .raffle import raffle, upload
