from flask import Blueprint, render_template, flash, redirect, url_for
from accounts.forms import LoginForm, RegistrationForm
from config import User, db

accounts_bp = Blueprint("accounts", __name__, template_folder="templates")


@accounts_bp.route("/registration", methods=["GET", "POST"])
def registration():

    form = RegistrationForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists", category="danger")
            return render_template("accounts/registration.html", form=form)

        new_user = User(
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            phone=form.phone.data,
            password=form.password.data,
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account Created", category="success")
        return redirect(url_for("accounts.login"))

    return render_template("accounts/registration.html", form=form)


# handles GET and POST requests
@accounts_bp.route("/login", methods=["GET", "POST"])
def login():
    # creates an instance of the LoginForm class
    form = LoginForm()

    # if the login form instance is validated
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # if user does not exist
        if not user:
            flash("User does not exist", category="danger")
            return render_template("accounts/login.html", form=form)

        # validate password
        if not user.validate_password(form.password.data):
            flash("Password is incorrect", category="danger")
            return render_template("accounts/login.html", form=form)

        flash("Login Successful", category="success")
        return redirect(url_for("posts.posts"))

    # pass form as parameter
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/account")
def account():
    return render_template("accounts/account.html")
