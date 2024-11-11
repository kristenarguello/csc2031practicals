from flask import Blueprint, render_template
from flask_login import login_required

from config import Log, logger
from decorators import roles_required

security_bp = Blueprint("security", __name__, template_folder="templates")


@security_bp.route("/security")
@login_required
@roles_required("sec_admin")
def security():
    all_logs = Log.query.all()
    try:
        with open("security.log") as f:
            print(f)
            general_logs = f.readlines()
            general_logs = general_logs[-10:]
            print(general_logs)
    except FileNotFoundError:
        logger.error("Log file not found!")
        general_logs = []

    return render_template(
        "security/security.html", logs=all_logs, general_logs=general_logs
    )
