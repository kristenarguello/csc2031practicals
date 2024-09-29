import secrets

from datetime import datetime
from flask import Flask, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

app = Flask(__name__)

# secret key for flask forms
app.config["SECRET_KEY"] = secrets.token_hex(16)

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///csc2031blog.db"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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


# database tables
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __init__(self, title, body):
        self.created = datetime.now()
        self.title = title
        self.body = body

    def update(self, title, body):
        self.created = datetime.now()
        self.title = title
        self.body = body
        db.session.commit()


# database admin
class MainIndexLink(MenuLink):
    def get_url(self):
        return url_for("index")


class PostView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ("id", "created", "title", "body")


admin = Admin(app, name="DB Admin", template_mode="bootstrap4")
admin._menu = admin._menu[1:]
admin.add_link(MainIndexLink(name="Home Page"))
admin.add_view(PostView(Post, db.session))


# import blueprints (after app because of circular import)
from accounts.views import accounts_bp
from posts.views import posts_bp
from security.views import security_bp

# register blueprints
app.register_blueprint(accounts_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(security_bp)
