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
            flash("Email already exists.", category="danger")
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

        flash(
            "Account Created. You must enable Multi-Factor Authentication (MFA) to login.",
            category="success",
        )
        return render_template(
            "accounts/setup_mfa.html",
            secret=new_user.mfa_key,
            uri=new_user.get_uri_mfa(),
        )

    return render_template("accounts/registration.html", form=form)


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

        # check if email and password are valid
        if user and user.validate_password(form.password.data):

            # check if key is valid
            if user.validate_mfa(form.mfa_key.data):

                # check if MFA is enabled when getting the key right
                if user.mfa_enabled is False:
                    # TODO: need to check if it's really changing in the db
                    user.mfa_enabled = True
                    db.session.commit()

                # got email, password and mfa right = login successful
                session["attempts"] = 0
                flash("Login Successful.", category="success")
                return redirect(url_for("posts.posts"))

            # check if MFA is not enabled when getting the key wrong
            elif user.mfa_enabled is False:
                flash(
                    "You have not enabled Multi-Factor Authentication. Please enable MFA to login.",
                    category="danger",
                )
                return render_template(
                    "accounts/setup_mfa.html",
                    secret=user.mfa_key,
                    uri=user.get_uri_mfa(),
                )

        # got something wrong - increase attempts
        session["attempts"] += 1
        form = authentication_attempts_limiter(session=session, form=form)

    # form was not valid or the number of attempts was exceeded
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/account")
def account():
    return render_template("accounts/account.html")


@accounts_bp.route("/unlock")
def unlock():
    session["attempts"] = 0
    return redirect(url_for("accounts.login"))


@accounts_bp.route("/mfa_setup")
def mfa_setup():
    return render_template("accounts/setup_mfa.html")
