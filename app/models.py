from datetime import datetime
from hashlib import md5
from time import time

from flask import current_app
from flask_login import UserMixin
import jwt
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app import db
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'))
    last_budget = db.relationship('Budget', foreign_keys=[last_budget_id])

    budgets = db.relationship('Budget', foreign_keys=[id], primaryjoin='Budget.user_id == User.id', backref=db.backref('user', uselist=False), lazy=True)

    
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    accounts = db.relationship('Account', backref='budget', lazy=True)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(9), db.CheckConstraint("type IN ('Asset', 'Liability', 'Equity', 'Income', 'Expense')", name='types'), nullable=False)

    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    parent = db.relationship('Account', backref='children', remote_side=[id], lazy=True)
    
    postings = db.relationship('Posting', backref='account', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Account {self.name}>'
    
    def balance(self, month=None):
        if month is None:
            return sum(account.balance() for account in self.children) + sum(posting.amount for posting in self.postings)
        else:
            return sum(account.balance(month=month) for account in self.children) + sum(posting.amount for posting in self.postings if posting.journal_entry.date.year == month.year and posting.journal_entry.date.month == month.month)


class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    payee = db.Column(db.String(255))
    description = db.Column(db.String(255))

    postings = db.relationship('Posting', backref='journal_entry', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Journal {self.description}>'


class Posting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal.id'), nullable=False)

    amount = db.Column(db.Numeric(precision=38, scale=28), nullable=False)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_type.id'), nullable=False)
    asset_type = db.relationship('AssetType')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Posting: {self.amount} to {self.account} for {self.journal_entry}>'


class AssetType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return self.name