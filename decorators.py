from functools import wraps

from flask import abort, flash
from flask_login import current_user

from utils import redirect_based_on_role


def roles_required(*roles):
    def inner_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # ta vindo 2 vezes aqui aaa
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return inner_decorator


def anonymous_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated:
            flash(
                "You are already logged in. Redirecting you to your main page.",
                category="info",
            )
            return redirect_based_on_role()
        return f(*args, **kwargs)

    return wrapped
