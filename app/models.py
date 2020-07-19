import time
from app import db, login_manager, bcrypt
from flask_login import UserMixin

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    todos = db.relationship("Todo", backref="user", lazy=True)

    def __repr__(self):
        return f"User({self.id}, '{self.username}')"
    
    def __str__(self):
        return self.username
    
    def get_user_id(self):
        return self.id
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id', ondelete='CASCADE'),
                        nullable=False)
    name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    week = db.Column(db.Integer)
    day = db.Column(db.Integer)
    finished = db.Column(db.Boolean, default=False)
    num_delayed = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Todo({self.id}, '{self.name}', {self.user})"

class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()