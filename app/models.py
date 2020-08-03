from flask import current_app
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(100))
    update_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Steps(db.Model):
    __tablename__ = 'steps'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    step1 = db.Column(db.String(250))
    step2 = db.Column(db.String(250))
    step3 = db.Column(db.String(250))
    steps = (step1, step2, step3)
    user = db.relationship('User', backref='user')

    def get_last_step(self):
        if not self.step1:
            return 1
        if not self.step2:
            return 2
        if not self.step3:
            return 3
    
    def __repr__(self):
        return '<Steps> {} {} {}'.format(self.step1, self.step2, self.step3)
