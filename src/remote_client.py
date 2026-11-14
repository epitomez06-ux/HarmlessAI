
import os
import json
import urllib.request
import urllib.error

from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env", override=True)

SERVER_URL = os.getenv(
    "HARMLESSAI_SERVER_URL",
    "http://127.0.0.1:5000"
).rstrip("/")

DEVICE_TOKEN = os.getenv(
    "HARMLESSAI_DEVICE_TOKEN",
    ""
).strip()


def send_activity(action, item_type, remote_path):
    if not DEVICE_TOKEN:
        print("HarmlessAI: Device is not enrolled yet.")
        return False

    if not SERVER_URL.startswith("https://"):
        if not SERVER_URL.startswith("http://127.0.0.1"):
            print("HarmlessAI: HTTPS is required for remote servers.")
            return False

    payload = {
        "action": action,
        "item_type": item_type,
        "path": str(remote_path)
    }

    request = urllib.request.Request(
        f"{SERVER_URL}/api/activity",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-HarmlessAI-Device-Token": DEVICE_TOKEN
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 201:
                return True

            print("HarmlessAI: Server rejected the activity.")
            return False

    except urllib.error.HTTPError as error:
        print(f"HarmlessAI: Server returned HTTP {error.code}.")
        return False

    except Exception:
        print("HarmlessAI: Could not connect to the server.")
        return False
