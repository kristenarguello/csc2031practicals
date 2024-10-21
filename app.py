from config import app
from flask import render_template


@app.route("/")
def index():
    return render_template("home/index.html")


@app.errorhandler(429)
def rate_limit(e):
    return render_template("errors/requests_limit.html"), 429


if __name__ == "__main__":
    app.run()
