from flask import render_template, request
from flask_login import current_user

from config import app, conditions, logger


@app.route("/")
def index():
    return render_template("home/index.html")


@app.errorhandler(429)
def rate_limit(e):
    logger.info(
        f"[User: {current_user.email}, Role: {current_user.role}, URL Requested: {request.url}, IP: {request.remote_addr}] Rate Limit."
    )
    return render_template("errors/rate_limit.html"), 429


@app.errorhandler(403)
def forbidden(e):
    logger.info(
        f"[User: {current_user.email}, Role: {current_user.role}, URL Requested: {request.url}, IP: {request.remote_addr}] Forbidden Access."
    )
    return render_template("errors/forbidden.html"), 403


# bad request
@app.errorhandler(400)
def bad_request(e):
    return render_template("errors/bad_request.html"), 400


# not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/not_found.html"), 404


# internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/internal_server_error.html"), 500


# not implemented
@app.errorhandler(501)
def not_implemented(e):
    return render_template("errors/not_implemented.html"), 501


@app.before_request
def firewall():
    for type, pattern in conditions.items():
        if pattern.search(request.path) or pattern.search(
            request.query_string.decode()
        ):
            return render_template("errors/attack_detected.html", label=type)


if __name__ == "__main__":
    app.run()
