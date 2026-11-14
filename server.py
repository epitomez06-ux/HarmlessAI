
import os
import secrets
import hmac
import hashlib
import time
from datetime import datetime
from functools import wraps

from flask import (
    Flask, request, jsonify, session,
    redirect, url_for, render_template
)
from dotenv import load_dotenv

from src.database import (
    initialize_database,
    register_device,
    authenticate_device,
    insert_activity,
    get_recent_activity,
    get_devices,
    revoke_device,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_DIR, ".env"), override=True)

app = Flask(__name__)

WEB_SECRET = os.getenv("HARMLESSAI_WEB_SECRET", "").strip()
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "").strip()
ENROLLMENT_CODE = os.getenv("HARMLESSAI_ENROLLMENT_CODE", "").strip()

if not WEB_SECRET:
    raise RuntimeError("HARMLESSAI_WEB_SECRET is not configured.")

app.secret_key = WEB_SECRET
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.getenv(
        "HARMLESSAI_COOKIE_SECURE", "false"
    ).lower() == "true",
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=32 * 1024,
)

# Basic per-process login lockout.
login_attempts = {}
LOCKOUT_SECONDS = 900
MAX_LOGIN_ATTEMPTS = 5

initialize_database()


def verify_web_password(password):
    try:
        algorithm, iterations, salt, expected_hash = (
            ADMIN_PASSWORD_HASH.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        if not 100000 <= iterations <= 2000000:
            return False

        salt_bytes = bytes.fromhex(salt)
        expected_bytes = bytes.fromhex(expected_hash)

        supplied_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            iterations,
        )

        return hmac.compare_digest(supplied_hash, expected_bytes)

    except (ValueError, TypeError):
        return False


def csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


def require_csrf():
    supplied = request.form.get("csrf_token", "")
    expected = session.get("_csrf_token", "")

    return (
        isinstance(supplied, str)
        and isinstance(expected, str)
        and bool(expected)
        and hmac.compare_digest(supplied, expected)
    )


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


@app.route("/", methods=["GET"])
def home():
    if session.get("admin_authenticated"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin_authenticated"):
        return redirect(url_for("dashboard"))

    client_ip = request.remote_addr or "unknown"
    now = time.monotonic()
    record = login_attempts.get(client_ip, {"count": 0, "until": 0})

    if record["until"] > now:
        return render_template(
            "login.html",
            error="Too many attempts. Please wait 15 minutes."
        ), 429

    error = None

    if request.method == "POST":
        if not require_csrf():
            return "Invalid security token. Reload the login page.", 400

        password = request.form.get("password", "")

        if isinstance(password, str) and verify_web_password(password):
            login_attempts.pop(client_ip, None)
            session.clear()
            session["admin_authenticated"] = True
            csrf_token()
            return redirect(url_for("dashboard"))

        record["count"] += 1

        if record["count"] >= MAX_LOGIN_ATTEMPTS:
            record["until"] = now + LOCKOUT_SECONDS

        login_attempts[client_ip] = record
        error = "Incorrect administrator password."

    return render_template("login.html", error=error)


@app.route("/admin/logout", methods=["POST"])
@admin_required
def logout():
    if not require_csrf():
        return "Invalid security token.", 400

    session.clear()
    return redirect(url_for("login"))


@app.route("/admin", methods=["GET"])
@admin_required
def dashboard():
    try:
        activities = get_recent_activity(100)
        devices = get_devices()

        return render_template(
            "dashboard.html",
            activities=activities,
            devices=devices,
        )
    except Exception:
        app.logger.exception("Dashboard data could not be loaded")
        return "Dashboard data is temporarily unavailable.", 503


@app.route("/admin/devices/<device_id>/revoke", methods=["POST"])
@admin_required
def revoke_enrolled_device(device_id):
    if not require_csrf():
        return "Invalid security token.", 400

    if len(device_id) > 100:
        return "Invalid device ID.", 400

    try:
        revoke_device(device_id)
        return redirect(url_for("dashboard"))
    except Exception:
        app.logger.exception("Device revocation failed")
        return "Could not revoke device.", 503


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "application": "HarmlessAI Cloud Server",
        "status": "running"
    })


@app.route("/api/enroll", methods=["POST"])
def enroll_device():
    if not ENROLLMENT_CODE:
        return jsonify({
            "error": "Device enrollment is not configured"
        }), 503

    data = request.get_json(silent=True) or {}

    supplied_code = data.get("enrollment_code", "")
    device_id = data.get("device_id", "")
    device_name = data.get("device_name", "")

    if not isinstance(supplied_code, str):
        return jsonify({"error": "Invalid enrollment code"}), 400

    if not hmac.compare_digest(supplied_code, ENROLLMENT_CODE):
        return jsonify({"error": "Invalid enrollment code"}), 401

    if not all(
        isinstance(value, str) and value.strip()
        for value in [device_id, device_name]
    ):
        return jsonify({"error": "Device information is required"}), 400

    if len(device_id) > 100 or len(device_name) > 100:
        return jsonify({"error": "Device information is too long"}), 400

    token = secrets.token_urlsafe(32)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    try:
        register_device(
            device_id.strip(),
            device_name.strip(),
            token,
            timestamp
        )

        return jsonify({
            "status": "device enrolled",
            "device_id": device_id.strip(),
            "device_token": token,
            "message": "Save this token securely. It will not be shown again."
        }), 201

    except Exception:
        app.logger.exception("Device enrollment failed")
        return jsonify({
            "error": "Could not enroll device. The device ID may already exist."
        }), 409


@app.route("/api/activity", methods=["POST"])
def receive_activity():
    supplied_token = request.headers.get(
        "X-HarmlessAI-Device-Token", ""
    )

    if not supplied_token:
        return jsonify({"error": "Device token required"}), 401

    try:
        device = authenticate_device(supplied_token)
    except Exception:
        app.logger.exception("Device authentication failed")
        return jsonify({"error": "Authentication service unavailable"}), 503

    if not device:
        return jsonify({"error": "Invalid or revoked device token"}), 401

    device_id, device_name = device
    data = request.get_json(silent=True) or {}

    action = data.get("action")
    item_type = data.get("item_type")
    path = data.get("path")

    if not all(
        isinstance(value, str) and value.strip()
        for value in [action, item_type, path]
    ):
        return jsonify({"error": "Invalid activity data"}), 400

    if len(action) > 30 or len(item_type) > 20 or len(path) > 2000:
        return jsonify({"error": "Activity data is too long"}), 400

    allowed_actions = {
        "CREATED",
        "MODIFIED",
        "DELETED",
        "RENAMED/MOVED"
    }

    if action not in allowed_actions:
        return jsonify({"error": "Unsupported activity"}), 400

    if item_type not in {"File", "Folder"}:
        return jsonify({"error": "Unsupported item type"}), 400

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    try:
        insert_activity(
            device_name,
            action,
            item_type,
            path,
            timestamp
        )

        return jsonify({
            "status": "activity received",
            "device_id": device_id
        }), 201

    except Exception:
        app.logger.exception("Could not save activity")
        return jsonify({"error": "Could not save activity"}), 500


if __name__ == "__main__":
    print("HARMLESSAI SERVER")
    print("Listening on port 5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
