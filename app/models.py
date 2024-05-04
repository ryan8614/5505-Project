from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwd_hash = db.Column(db.String(255), nullable=False)

    def verify_password(self, password):
        return check_password_hash(self.passwd_hash, password)

    def get_id(self):
        return str(self.id)
    
