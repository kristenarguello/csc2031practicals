import logging
import secrets
from datetime import datetime
from typing import override

import pyotp
from flask import Flask, abort, flash, redirect, request, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import LoginManager, UserMixin, current_user
from flask_migrate import Migrate
from flask_qrcode import QRcode
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

app = Flask(__name__)

# secret key for flask forms
app.config["SECRET_KEY"] = secrets.token_hex(16)

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///csc2031blog.db"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# recaptcha configuration
app.config["RECAPTCHA_PUBLIC_KEY"] = "6Lcur1oqAAAAADss3xvAdVlpRqlt1pSf43nskd-K"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6Lcur1oqAAAAAAfoao99Z-fuC3x4m8YpirBqQ1Rm"

# flask admin configuration
app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

# set up login configuration
login_manager = LoginManager()
login_manager.login_view = "/login"  # type: ignore
login_manager.login_message = "You must be logged in to access this page."
login_manager.login_message_category = "danger"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id: int):
    return User.query.get(int(id))


# database tables
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("users.id"))
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user = db.relationship("User", back_populates="posts")

    def __init__(self, userid, title, body):
        self.created = datetime.now()
        self.userid = userid
        self.title = title
        self.body = body

    def update(self, title, body):
        self.created = datetime.now()
        self.title = title
        self.body = body
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    mfa_key = db.Column(db.String(32), nullable=False, default=pyotp.random_base32())
    mfa_enabled = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(100), nullable=False, default="end_user")

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)

    # User posts
    posts = db.relationship("Post", order_by=Post.id, back_populates="user")

    # logs
    log = db.relationship("Log", uselist=False, back_populates="user")

    # UserMixin attributes
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, email, firstname, lastname, phone, password):
        self.email = email
        self.password = password
        self.mfa_key = pyotp.random_base32()
        self.mfa_enabled = False
        self.role = "end_user"
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone

    def validate_password(self, password):
        return self.password == password

    def validate_mfa(self, token):
        totp = pyotp.TOTP(self.mfa_key)
        return totp.verify(token)

    def get_uri_mfa(self):
        return str(
            str(
                pyotp.totp.TOTP(self.mfa_key).provisioning_uri(
                    self.email, "CSC2031 Blog"
                )
            )
        )

    # user mixin properties
    @property
    def is_active(self):
        return self.active

    def generate_log(self):
        log = Log(self.id)
        db.session.add(log)
        db.session.commit()
        return log

    def update_log(self):
        if self.log is None:  # when the user is loggin in but log not created before
            self.generate_log()

        self.log.previous_login = self.log.latest_login  # type: ignore
        self.log.previous_ip = self.log.latest_ip  # type: ignore

        self.log.latest_login = datetime.now()  # type: ignore
        self.log.latest_ip = request.remote_addr  # type: ignore

        db.session.commit()


class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("users.id"))

    registered_on = db.Column(db.DateTime, nullable=False)

    latest_login = db.Column(db.DateTime, nullable=True)
    previous_login = db.Column(db.DateTime, nullable=True)

    # flask request object: request.remote_addr
    latest_ip = db.Column(db.String(100), nullable=True)
    previous_ip = db.Column(db.String(100), nullable=True)

    user = db.relationship("User", back_populates="log")

    def __init__(self, userid):
        self.userid = userid
        self.registered_on = datetime.now()


# database admin
class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for("index")


class PostView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ("id", "userid", "created", "title", "body", "user")

    can_create = False
    can_edit = False
    can_delete = False

    @override
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "db_admin"

    @override
    def inaccessible_callback(self, name, **kwargs):  # type: ignore
        if current_user.is_authenticated:
            abort(403)
        # if anonymous
        flash("Administrator access required.", category="danger")
        return redirect(url_for("accounts.login"))


class UserView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_list = (
        "id",
        "email",
        "password",
        "mfa_key",
        "mfa_enabled",
        "firstname",
        "lastname",
        "phone",
        "posts",
    )

    @override
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "db_admin"

    @override
    def inaccessible_callback(self, name, **kwargs):  # type: ignore
        if current_user.is_authenticated:
            abort(403)
        # if anonymous
        flash("Administrator access required.", category="danger")
        return redirect(url_for("accounts.login"))


# TODO: delete this before final submission
class LogView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = (
        "id",
        "userid",
        "registered_on",
        "latest_login",
        "previous_login",
        "latest_ip",
        "previous_ip",
        "user",
    )

    @override
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "db_admin"

    @override
    def inaccessible_callback(self, name, **kwargs):  # type: ignore
        if current_user.is_authenticated:
            abort(403)
        # if anonymous
        flash("Administrator access required.", category="danger")
        return redirect(url_for("accounts.login"))


admin = Admin(app, name="DB Admin", template_mode="bootstrap4")
admin._menu = admin._menu[1:]
admin.add_link(MainIndexLink(name="Home Page"))
admin.add_view(PostView(Post, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(LogView(Log, db.session))


# app wide default rate limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["500 per day"],
)

# set up mfa qr code
qrcode = QRcode(app)

# set up logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("security.log", "a")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


# import blueprints (after app because of circular import)
from accounts.views import accounts_bp
from posts.views import posts_bp
from security.views import security_bp

# register blueprints
app.register_blueprint(accounts_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(security_bp)
