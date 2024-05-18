from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import binascii, os

# Import configuration
from .config import Config

# Initialize extension
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Make sure the key is configured before app initialization
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = binascii.hexlify(os.urandom(24)).decode()

    # Initialize database and migration module
    db.init_app(app)
    migrate.init_app(app, db)

    # Config Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprint
    from app.Blueprint.auth import auth_bp as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.Blueprint.pages import pages_bp as pages_blueprint
    app.register_blueprint(pages_blueprint, url_prefix='/')

    from app.Blueprint.raffle import raffle_bp as raffle_blueprint
    app.register_blueprint(raffle_blueprint, url_prefix='/raffle')

    from app.Blueprint.trade import trade_bp as trade_blueprint
    app.register_blueprint(trade_blueprint, url_prefix='/trade')

    return app
