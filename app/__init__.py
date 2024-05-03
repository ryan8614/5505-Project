from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
import binascii, os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
# secret_key = binascii.hexlify(os.urandom(24)).decode()
app.config['SECRET_KEY'] = 'secret_key'

app.config.from_object(Config)
db = SQLAlchemy(app)
Migrate = Migrate(app, db)

from app import routes, models