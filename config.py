import secrets
from datetime import datetime

import pyotp
from flask import Flask, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import LoginManager, UserMixin
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

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)

    # User posts
    posts = db.relationship("Post", order_by=Post.id, back_populates="user")

    # UserMixin attributes
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, email, firstname, lastname, phone, password):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.mfa_key = pyotp.random_base32()
        self.mfa_enabled = False

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


# database admin
class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for("index")


class PostView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ("id", "userid", "created", "title", "body", "user")


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


admin = Admin(app, name="DB Admin", template_mode="bootstrap4")
admin._menu = admin._menu[1:]
admin.add_link(MainIndexLink(name="Home Page"))
admin.add_view(PostView(Post, db.session))
admin.add_view(UserView(User, db.session))


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

# import blueprints (after app because of circular import)
from accounts.views import accounts_bp
from posts.views import posts_bp
from security.views import security_bp

# register blueprints
app.register_blueprint(accounts_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(security_bp)
