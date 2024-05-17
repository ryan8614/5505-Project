from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
from .ImageProcessor import ImageProcessor
import binascii, os


app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

secret_key = binascii.hexlify(os.urandom(24)).decode()
app.config['SECRET_KEY'] = secret_key

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Set the upload and output directories 
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

processor = ImageProcessor(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])

from app import routes, models