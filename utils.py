from flask import redirect, url_for
from flask_login import current_user


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
