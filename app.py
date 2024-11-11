from flask import render_template, request
from flask_login import current_user

from config import app, logger


@app.route("/")
def index():
    return render_template("home/index.html")


@app.errorhandler(429)
def rate_limit(e):
    logger.info(
        f"[User: {current_user.email}, Role: {current_user.role}, URL Requested: {request.url}, IP: {request.remote_addr}] Rate Limit."
    )
    return render_template("errors/rate_limit.html")


@app.errorhandler(403)
def forbidden(e):
    logger.info(
        f"[User: {current_user.email}, Role: {current_user.role}, URL Requested: {request.url}, IP: {request.remote_addr}] Forbidden Access."
    )
    return render_template("errors/forbidden.html")


@app.errorhandler(404)
def page_not_found(e):
    logger.info(
        f"[User: {current_user.email}, Role: {current_user.role}, URL Requested: {request.url}, IP: {request.remote_addr}] Page Not Found."
    )
    return render_template("errors/not_found.html")


if __name__ == "__main__":
    app.run()
