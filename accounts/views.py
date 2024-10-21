from flask import Blueprint, flash, redirect, render_template, session, url_for
from markupsafe import Markup

from accounts.forms import LoginForm, RegistrationForm
from config import User, db, limiter

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


# keep track of users invalid authentication attempts
# maximum permitted attempts = 3
# invalid authentication should contain the number of permitted attempts left
# login form should be hidden when the maximum number of permitted invalid authentication attempts is reached - simulate the users account being locked
# provide a link to the user to simulate the unlocking of the users account - reset to 3 permitted attempts


def authentication_attempts_limiter(session, form):
    """
    Limit the number of authentication attempts.
    Returns the login form if the number of attempts
    is less than 3 and None if the number of attempts
    is greater than or equal to 3.
    """
    if session["attempts"] >= 3:
        flash(
            Markup(
                "Number of incorrect login attempts exceeded. Please click <a href='/unlock'>here</a> to unlock your account."
            ),
            category="danger",
        )
        # hide login form
        return None
    flash(
        f"Please check your login credentials and try again. You have {3 - session['attempts']} attempts left.",
        category="danger",
    )
    return form


# when reloading the page the form reappears but the session is not reset
@accounts_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def login():
    # check if authentication attempts is in session
    if "attempts" not in session:
        session["attempts"] = 0

    # creates an instance of the LoginForm class
    form = LoginForm()

    # if the login form instance is validated
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # if user does not exist
        if not user or not user.validate_password(form.password.data):
            session["attempts"] += 1
            form = authentication_attempts_limiter(session=session, form=form)
            return render_template("accounts/login.html", form=form)

        # reset attempts
        session["attempts"] = 0
        flash("Login Successful", category="success")
        return redirect(url_for("posts.posts"))

    # pass form as parameter
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/account")
def account():
    return render_template("accounts/account.html")


@accounts_bp.route("/unlock")
def unlock():
    session["attempts"] = 0
    return redirect(url_for("accounts.login"))
