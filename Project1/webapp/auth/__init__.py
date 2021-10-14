import functools
from flask import flash, redirect, url_for, session, abort
from flask_login import LoginManager, AnonymousUserMixin
from flask_login import current_user
from flask_openid import OpenID

from flask_bcrypt import Bcrypt

class BlogAnonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = "Guest"

bcrypt = Bcrypt()
oid = OpenID()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"


@login_manager.user_loader 
def load_user(userid):
    from models import User
    return User.query.get(userid)


def create_module(app, **kwargs):
    bcrypt.init_app(app)
    oid.init_app(app)
    login_manager.init_app(app)
    from .controllers import auth_blueprint
    app.register_blueprint(auth_blueprint)