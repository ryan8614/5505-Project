import os
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import column_property
from sqlalchemy import func
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
    owner INTEGER REFERENCES users(id),
    bonus NUMERIC CHECK (bonus>=0)
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
    frag_id TEXT NOT NULL,
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
    bonus = db.Column(db.String(255), nullable=False, default='50.0')

    __table_args__ = (
        db.CheckConstraint('pieces IN (4, 6, 9)', name='check_pieces_values'),
    )

    def __repr__(self):
        return f'<NFT {self.path}>'
    
    def set_bonus(self, value):
        self.bonus = str(Decimal(value))

    def get_bonus(self):
        return Decimal(self.bonus)
    
    @hybrid_property
    def name(self):
        """Extracts the file name without extension from the path."""
        if 'static/uploads/' in self.path:
            # Extract the file part of the path after 'static/outputs/'
            file_name_with_extension = self.path.split('static/uploads/')[-1]
            # Use os.path.splitext to remove the file extension
            file_name, _ = os.path.splitext(file_name_with_extension)
            return file_name
        return None  



class Fragment(db.Model):
    __tablename__ = 'fragment'

    id = db.Column(db.String(64), primary_key=True)
    img_id = db.Column(db.String(64), db.ForeignKey('nft.id'))
    path = db.Column(db.String(255), unique=True, nullable=False)
    piece_number = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.CheckConstraint('piece_number BETWEEN 1 AND 9'),
    )
    
    # Add a one-to-one relationship with Trade
    trade = db.relationship('Trade', backref='fragment', uselist=False, lazy='joined', cascade='all, delete', passive_deletes=True, primaryjoin="Fragment.id==Trade.id")

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
    
    
    def verify_frag_name(self):
        """
        Verify that the SHA-256 hash of the complete filename (with extension) matches the 'id' of the fragment.
        """
        if 'static/outputs/' in self.path:
            # Extract the complete file name with extension
            file_name_with_extension = self.path.split('static/outputs/')[-1]
            # Compute the SHA-256 hash of the complete filename
            sha256_hash = hashlib.sha256(file_name_with_extension.encode()).hexdigest()
            # Check if the computed hash matches the id
            return sha256_hash == self.id
        return False



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
    


class TradeHistory(db.Model):
    __tablename__ = 'trade_history'
    
    # Existing fields
    trade_id = db.Column(db.Integer, primary_key=True)
    frag_id = db.Column(db.Text,  nullable=False)
    frag_name = db.Column(db.Text,  nullable=False)
    seller = db.Column(db.Integer, db.ForeignKey('users.id'))
    buyer = db.Column(db.Integer, db.ForeignKey('users.id'))
    price = db.Column(db.String, nullable=False, default=0.0, server_default="0.0")
    transaction_time = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    # Relationships
    seller_user = db.relationship('User', foreign_keys=[seller], backref=db.backref('sold_transactions', lazy='dynamic'))
    buyer_user = db.relationship('User', foreign_keys=[buyer], backref=db.backref('bought_transactions', lazy='dynamic'))

    __table_args__ = (
        db.CheckConstraint(price >= 0, name='price_nonnegative'),
    )

    def __repr__(self):
        return f"<TradeHistory(trade_id={self.trade_id}, frag_id={self.frag_id}, seller={self.seller}, buyer={self.buyer}, price={self.price}, transaction_time={self.transaction_time})>"
    
    def set_price(self, value):
        self.price = str(Decimal(value))

    def get_price(self):
        return Decimal(self.price)
    
    @property
    def seller_username(self):
        return User.query.get(self.seller).username

    @property
    def buyer_username(self):
        return User.query.get(self.buyer).username