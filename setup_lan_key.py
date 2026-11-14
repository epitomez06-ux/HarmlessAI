import secrets
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

lines = ENV_FILE.read_text(encoding="utf-8").splitlines()

lines = [
    line for line in lines
    if not line.startswith("HARMLESSAI_LAN_KEY=")
]

new_key = secrets.token_urlsafe(32)
lines.append(f"HARMLESSAI_LAN_KEY={new_key}")

ENV_FILE.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

print("A new LAN key was saved in .env.")
print("Keep this key private.")