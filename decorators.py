from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def roles_required(*roles):
    def inner_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return inner_decorator


def anonymous_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already logged in.", category="info")
            return redirect(url_for("posts.posts"))
        return f(*args, **kwargs)

    return wrapped
