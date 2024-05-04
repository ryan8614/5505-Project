from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
import binascii, os


app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# secret_key = binascii.hexlify(os.urandom(24)).decode()
app.config['SECRET_KEY'] = 'you-will-never-guess-the-secret_key'

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

from app import routes, models