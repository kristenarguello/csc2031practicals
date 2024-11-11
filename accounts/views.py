from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, logout_user

from accounts.forms import LoginForm, RegistrationForm
from accounts.utils import authentication_attempts_limiter, login_and_redirect
from config import User, db, limiter, logger, ph
from decorators import anonymous_required

accounts_bp = Blueprint("accounts", __name__, template_folder="templates")


@accounts_bp.route("/registration", methods=["GET", "POST"])
@anonymous_required
def registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists.", category="danger")
            return render_template("accounts/registration.html", form=form)

        password_hash = ph.hash(form.password.data)
        new_user = User(
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            phone=form.phone.data,
            password=password_hash,
        )

        db.session.add(new_user)
        db.session.commit()

        new_user.generate_log()
        logger.info(
            f"[User: {new_user.email}, Role: {new_user.role}, IP: {request.remote_addr}] Successful Registration."
        )

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


# when reloading the page the form reappears but the session is not reset
@accounts_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute")
@anonymous_required
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
                    user.mfa_enabled = True
                    db.session.commit()

                return login_and_redirect(user)

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
        logger.info(
            f"[User: {form.email.data}, Attempts: {session["attempts"]}, IP: {request.remote_addr}] Invalid Login Attempt."
        )
        form = authentication_attempts_limiter(session=session, form=form, user=user)

    # form was not valid or the number of attempts was exceeded
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/account")
@login_required
def account():
    return render_template("accounts/account.html")


@accounts_bp.route("/unlock")
@anonymous_required
def unlock():
    session["attempts"] = 0
    return redirect(url_for("accounts.login"))


@accounts_bp.route("/mfa_setup")
@anonymous_required
def mfa_setup():
    return render_template("accounts/setup_mfa.html")


@accounts_bp.route("/logout")
@login_required
def logout():
    email = current_user.email
    role = current_user.role
    logout_user()

    logger.info(f"[User: {email}, Role: {role}] Successful Log Out.")
    return redirect(url_for("index"))
