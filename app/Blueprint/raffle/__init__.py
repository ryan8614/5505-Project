from flask import Blueprint
from ...ImageProcessor import ImageProcessor
import os

# Create a Blueprint for raffle
raffle_bp = Blueprint('raffle', __name__, template_folder='../../templates')

# Create the required directories
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/outputs', exist_ok=True)

# Initialize image processor
processor = ImageProcessor('static/uploads', 'static/outputs')

# Import all view functions from raffle.py in the current directory
from .raffle import raffle, upload
