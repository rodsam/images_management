from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, loginmanager, Config

class User(db.Model, UserMixin):
    '''
    User Model
    '''

    __tablename__ = 'user'

    id = db.Column(db.Integer, autoincrement= True , primary_key= True, unique= True)
    username = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))
    admin_power = db.Column(db.Integer, default= 0)
    address = db.Column(db.String(256))
    email = db.Column(db.String(128))

    last_seen = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        if self.admin_power == 1:
            return True
        elif isinstance(Config.ADMINS, list):
            return self.username in Config.ADMINS
        elif isinstance(Config.ADMINS, str):
            return self.username == Config.ADMINS
        else:
            return False


@loginmanager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Image(db.Model):
    '''
    Image Model
    '''
    __tablename__ = 'image'

    id = db.Column(db.Integer, autoincrement=True, primary_key= True, unique= True)
    title = db.Column(db.String(50))
    src = db.Column(db.String(256))
    description = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', uselist=False,foreign_keys=[user_id])
    created_at = db.Column(db.DateTime, default=datetime.now)


class Comment(db.Model):
    '''
    Comment Model
    '''
    __tablename__ = 'comment'

    id = db.Column(db.Integer, autoincrement= True, primary_key= True, unique= True)
    content = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    post_by = db.relationship('User', uselist= False, foreign_keys=[user_id])
    comment_on = db.relationship('Image', uselist=False, foreign_keys=[image_id])
    created_at = db.Column(db.DateTime, default=datetime.now)
