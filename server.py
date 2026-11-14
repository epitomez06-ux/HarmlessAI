
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime
import sqlite3
import os

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
DATABASE = PROJECT_DIR / "data" / "remote_activity.db"

load_dotenv(PROJECT_DIR / ".env")

app = Flask(__name__)

API_KEY = os.getenv("HARMLESSAI_LAN_KEY", "")


def initialize_database():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                action TEXT NOT NULL,
                item_type TEXT NOT NULL,
                path TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "application": "HarmlessAI LAN Server",
        "status": "running"
    })


@app.route("/api/activity", methods=["POST"])
def receive_activity():
    if not API_KEY:
        return jsonify({"error": "Server authentication is not configured"}), 503

    supplied_key = request.headers.get("X-HarmlessAI-Key", "")

    if not supplied_key or supplied_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    device_name = data.get("device_name")
    action = data.get("action")
    item_type = data.get("item_type")
    path = data.get("path")

    if not all(isinstance(value, str) and value.strip()
               for value in [device_name, action, item_type, path]):
        return jsonify({"error": "Invalid activity data"}), 400

    if len(device_name) > 100 or len(action) > 30:
        return jsonify({"error": "Activity data is too long"}), 400

    if len(item_type) > 20 or len(path) > 2000:
        return jsonify({"error": "Activity data is too long"}), 400

    allowed_actions = {
        "CREATED", "MODIFIED", "DELETED", "RENAMED/MOVED"
    }

    if action not in allowed_actions:
        return jsonify({"error": "Unsupported activity"}), 400

    if item_type not in {"File", "Folder"}:
        return jsonify({"error": "Unsupported item type"}), 400

    timestamp = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            INSERT INTO activity
            (device_name, action, item_type, path, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (device_name, action, item_type, path, timestamp))

    return jsonify({"status": "activity received"}), 201


if __name__ == "__main__":
    initialize_database()

    print("HARMLESSAI LAN SERVER")
    print("Listening on port 5000")
    print("Keep this window open while the server is running.")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
