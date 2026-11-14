
import os
import json
import uuid
import urllib.request
import urllib.error

from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

SERVER_URL = os.getenv(
    "HARMLESSAI_SERVER_URL",
    "http://127.0.0.1:5000"
).rstrip("/")

ENROLLMENT_CODE = os.getenv(
    "HARMLESSAI_ENROLLMENT_CODE",
    ""
).strip()


def main():
    if not ENROLLMENT_CODE:
        print("Enrollment secret is missing from the admin .env file.")
        return

    if not (
        SERVER_URL.startswith("https://")
        or SERVER_URL.startswith("http://127.0.0.1")
    ):
        print("Use HTTPS for a remote cloud server.")
        return

    device_name = input("Enter the computer name to enroll: ").strip()

    if not device_name or len(device_name) > 100:
        print("Invalid device name.")
        return

    device_id = str(uuid.uuid4())

    payload = {
        "enrollment_code": ENROLLMENT_CODE,
        "device_id": device_id,
        "device_name": device_name
    }

    request = urllib.request.Request(
        f"{SERVER_URL}/api/enroll",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))

        token = result.get("device_token")

        if not token:
            print("Enrollment failed: no device token received.")
            return

        token_folder = PROJECT_DIR / "device_tokens"
        token_folder.mkdir(exist_ok=True)

        token_file = token_folder / f"{device_id}.env"
        token_file.write_text(
            f"HARMLESSAI_SERVER_URL={SERVER_URL}\n"
            f"HARMLESSAI_DEVICE_TOKEN={token}\n",
            encoding="utf-8"
        )

        print("Device enrolled successfully.")
        print(f"Device name: {device_name}")
        print(f"Device ID: {device_id}")
        print(f"Private token file created: {token_file}")
        print("Transfer this file securely to the enrolled computer.")
        print("Never share the enrollment secret or device token.")

    except urllib.error.HTTPError as error:
        print(f"Enrollment failed. HTTP status: {error.code}")
    except Exception:
        print("Could not connect to the HarmlessAI server.")


if __name__ == "__main__":
    main()
