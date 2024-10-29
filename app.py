from config import app
from flask import render_template


@app.route("/")
def index():
    return render_template("home/index.html")


@app.errorhandler(429)
def rate_limit(e):
    return render_template("errors/rate_limit.html"), 429


@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/forbidden.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/not_found.html"), 404


if __name__ == "__main__":
    app.run()
