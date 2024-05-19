import os
import hashlib
from werkzeug.security import check_password_hash
from flask import g
from flask_login import UserMixin
from sqlalchemy import func, Numeric
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.hybrid import hybrid_property 
from . import db

'''
CREATE TABLE fragment (
        id VARCHAR(64) NOT NULL, 
        img_id VARCHAR(64), 
        path VARCHAR(255) NOT NULL, 
        piece_number INTEGER NOT NULL, 
        owner INTEGER, 
        PRIMARY KEY (id), 
        CHECK (piece_number BETWEEN 1 AND 9), 
        FOREIGN KEY(img_id) REFERENCES nft (id), 
        UNIQUE (path), 
        FOREIGN KEY(owner) REFERENCES users (id)
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    passwd_hash VARCHAR(255) NOT NULL,
    balance NUMERIC(10, 2) NOT NULL DEFAULT 50.00,
    CONSTRAINT check_balance CHECK (balance >= 0 AND balance < 100000)
);
CREATE TABLE nft (
        id VARCHAR(64) NOT NULL, 
        path VARCHAR(255) NOT NULL, 
        completed BOOLEAN NOT NULL, 
        pieces INTEGER NOT NULL, 
        owner INTEGER, 
        bonus NUMERIC(10, 2) NOT NULL DEFAULT 100.00,
        PRIMARY KEY (id), 
        CONSTRAINT check_pieces_values CHECK (pieces IN (4, 6, 9)), 
        UNIQUE (path), 
        FOREIGN KEY(owner) REFERENCES users (id)
);
CREATE TABLE trade (
        id VARCHAR(64) NOT NULL, 
        owner INTEGER, 
        price NUMERIC(10, 2) NOT NULL, 
        listed_time DATETIME, 
        PRIMARY KEY (id), 
        CHECK (price >= 0), 
        FOREIGN KEY(id) REFERENCES fragment (id), 
        FOREIGN KEY(owner) REFERENCES users (id)
);
CREATE TABLE trade_history (
        trade_id INTEGER NOT NULL, 
        frag_id TEXT NOT NULL, 
        frag_name TEXT NOT NULL, 
        seller INTEGER, 
        buyer INTEGER, 
        price NUMERIC(10, 2) NOT NULL,
        transaction_time DATETIME NOT NULL, 
        PRIMARY KEY (trade_id), 
        CONSTRAINT price_nonnegative CHECK (price >= 0), 
        FOREIGN KEY(seller) REFERENCES users (id), 
        FOREIGN KEY(buyer) REFERENCES users (id)
);
'''

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwd_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=50.00, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def verify_password(self, password):
        return check_password_hash(self.passwd_hash, password)

    # Fragments owned by User
    user_fragments = db.relationship('Fragment', lazy='select')

    # Transaction initiated by user
    user_transactions = db.relationship('Trade', lazy='select')

    __table_args__ = (
        db.CheckConstraint('balance >= 0 AND balance < 100000', name='check_balance'),
    )
    
    def set_balance(self, value):
        # Directly assign the Decimal value
        if isinstance(value, Decimal):
            self.balance = value
        else:
            self.balance = Decimal(value)

    def get_balance(self):
        return self.balance



class NFT(db.Model):
    __tablename__ = 'nft'

    id = db.Column(db.String(64), primary_key=True)  # Use a hash of the file name as the primary key
    path = db.Column(db.String(255), unique=True, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    pieces = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    bonus = db.Column(db.Numeric(10, 2), default=Decimal('100.00'), nullable=False)

    __table_args__ = (
        db.CheckConstraint('pieces IN (4, 6, 9)', name='check_pieces_values'),
    )

    def __repr__(self):
        return f'<NFT {self.path}>'
    
    def set_bonus(self, value):
        # Directly assign the Decimal value
        if isinstance(value, Decimal):
            self.balance = value
        else:
            self.balance = Decimal(value)

    @hybrid_property
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
    
    @name.expression
    def name(cls):
        """Extract the file name in the path (without extension) in SQL, suitable for SQLite database."""
        start = func.instr(cls.path, 'static/outputs/') + len('static/outputs/')
        rest_of_path = func.substr(cls.path, start)
        dot_pos = func.instr(rest_of_path, '.')
        return func.substr(rest_of_path, 1, dot_pos - 1)

    
    
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
    price = db.Column(db.Numeric(10, 2), nullable=False,  default='0.0')
    listed_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint('price >= 0'),
    )

    def set_price(self, value):
        # Directly assign the Decimal value
        if isinstance(value, Decimal):
            self.price = value
        else:
            self.price = Decimal(value)

    def get_price(self):
        return self.price
    


class TradeHistory(db.Model):
    __tablename__ = 'trade_history'
    
    # Existing fields
    trade_id = db.Column(db.Integer, primary_key=True)
    frag_id = db.Column(db.Text,  nullable=False)
    frag_name = db.Column(db.Text,  nullable=False)
    seller = db.Column(db.Integer, db.ForeignKey('users.id'))
    buyer = db.Column(db.Integer, db.ForeignKey('users.id'))
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0, server_default="0.0")
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
        # Directly assign the Decimal value
        if isinstance(value, Decimal):
            self.price = value
        else:
            self.price = Decimal(value)

    def get_price(self):
        return self.balance
    
    @property
    def seller_username(self):
        return User.query.get(self.seller).username

    @property
    def buyer_username(self):
        return User.query.get(self.buyer).username