from flask import flash, redirect, session, url_for
from flask_login import current_user, login_user
from markupsafe import Markup

from config import db


def redirect_based_on_role():
    """
    Redirects the just logged in user based on their role.
    """
    if current_user.role == "db_admin":
        return redirect(url_for("admin.index"))
    elif current_user.role == "sec_admin":
        return redirect(url_for("security.security"))
    else:
        return redirect(url_for("posts.posts"))


def login_and_redirect(user):
    """
    Logs in the user and sets the session attempts to 0.
    And then, redirects the user based on their role.
    """
    # got email, password and mfa right = login successful
    logged = login_user(user)
    print(f"User logged in: {logged} - session _user_id: {session['_user_id']}")
    if logged is False:
        flash(
            "Something happened, login failed. Please try again.",
            category="danger",
        )
        return redirect(url_for("accounts.login"))
    session["attempts"] = 0
    flash("Login Successful.", category="success")
    return redirect_based_on_role()


def authentication_attempts_limiter(session, form, user):
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
        # TODO: user may not log in using credentials from an inactive account
        # user.active = False
        # db.session.commit()

        # hide login form
        return None
    flash(
        f"Please check your login credentials and try again. You have {3 - session['attempts']} attempts left.",
        category="danger",
    )
    return form
