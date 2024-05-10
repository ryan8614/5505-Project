import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.hybrid import hybrid_property
from . import db

'''
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) UNIQUE,
    email VARCHAR(255) UNIQUE,
    passwd_hash VARCHAR(255),
    balance NUMERIC CHECK (balance >=0 AND balance < 100000)
);

CREATE TABLE nft (
    id TEXT PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    completed INTEGER DEFAULT 0 NOT NULL CHECK (completed IN (0, 1)),
    pieces INTEGER NOT NULL CHECK (pieces IN (4, 6, 9)),
    owner INTEGER REFERENCES users(id)
);

CREATE TABLE fragment (
    id TEXT PRIMARY KEY,
    img_id TEXT REFERENCES nft(id),
    path TEXT UNIQUE NOT NULL,
    piece_number INTEGER CHECK (piece_number BETWEEN 1 AND 9),
    owner INTEGER REFERENCES users(id)
);

CREATE TABLE trade (
    id TEXT PRIMARY KEY REFERENCES fragment(id), 
    owner INTEGER REFERENCES users(id),
    price NUMERIC CHECK (price>=0),
    listed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE trade_history (
    trade_id INTEGER PRIMARY KEY,
    frag_id TEXT NOT NULL REFERENCES fragment(id),
    seller INTEGER REFERENCES users(id),
    buyer INTEGER REFERENCES users(id),
    price NUMERIC CHECK (price>=0),
    transaction_time TIMESTAMP NOT NULL
);
'''


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwd_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.String(255), nullable=False, default='50.0')

    # Fragments owned by User
    user_fragments = db.relationship('Fragment', lazy='select')

    # Transaction initiated by user
    user_transactions = db.relationship('Trade', lazy='select')

    __table_args__ = (
        db.CheckConstraint('balance >= 0 AND balance < 100000', name='check_balance'),
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def verify_password(self, password):
        return check_password_hash(self.passwd_hash, password)
    
    def set_balance(self, value):
        self.balance = str(Decimal(value))

    def get_balance(self):
        return Decimal(self.balance)

    

class NFT(db.Model):
    __tablename__ = 'nft'

    id = db.Column(db.String(64), primary_key=True)  # Use a hash of the file name as the primary key
    path = db.Column(db.String(255), unique=True, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    pieces = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.CheckConstraint('pieces IN (4, 6, 9)', name='check_pieces_values'),
    )

    def __repr__(self):
        return f'<NFT {self.path}>'
    


class Fragment(db.Model):
    __tablename__ = 'fragment'

    id = db.Column(db.String(64), primary_key=True)
    img_id = db.Column(db.String(64))
    path = db.Column(db.String(255), unique=True, nullable=False)
    piece_number = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.CheckConstraint('piece_number BETWEEN 1 AND 9'),
    )
    
    # Add a one-to-one relationship with Trade
    trade = db.relationship('Trade', backref='fragment', uselist=False, lazy='joined', primaryjoin="Fragment.id==Trade.id")

    @hybrid_property
    def trade_price(self):
        if self.trade:
            return 'For Sale', self.trade.get_price()
        return 'Not For Sale', -1
    
    @hybrid_property
    def name(self):
        """Extracts the file name without extension from the path."""
        if 'static/outputs/' in self.path:
            # Extract the file part of the path after 'static/outputs/'
            file_name_with_extension = self.path.split('static/outputs/')[-1]
            # Use os.path.splitext to remove the file extension
            file_name, _ = os.path.splitext(file_name_with_extension)
            return file_name
        return None  



class Trade(db.Model):
    __tablename__ = 'trade'

    id = db.Column(db.String(64),  db.ForeignKey('fragment.id'), primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    price = db.Column(db.String(255), nullable=False, default='0.0')
    listed_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint('price >= 0'),
    )

    def set_price(self, value):
        self.price = str(Decimal(value))

    def get_price(self):
        return Decimal(self.price)
    


