
import json
import os
import platform
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env", override=True)

SERVER_URL = os.getenv(
    "HARMLESSAI_SERVER_URL",
    "http://192.168.254.108:5000"
)

API_KEY = os.getenv("HARMLESSAI_LAN_KEY", "")
DEVICE_NAME = platform.node()


def send_activity(action, item_type, path):
    if not API_KEY:
        print("Remote authentication key is not configured.")
        return False

    data = {
        "device_name": DEVICE_NAME,
        "action": action,
        "item_type": item_type,
        "path": str(path)
    }

    payload = json.dumps(data).encode("utf-8")

    request = Request(
        f"{SERVER_URL}/api/activity",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-HarmlessAI-Key": API_KEY
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=5) as response:
            return response.status == 201

    except (URLError, HTTPError, TimeoutError) as error:
        print(f"Remote activity could not be sent: {error}")
        return False
