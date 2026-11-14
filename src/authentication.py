
import os
import hashlib
import hmac
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

console = Console()

PROJECT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_DIR / ".env"

load_dotenv(ENV_FILE, override=True)



def verify_admin():
    console.print("\n[bold cyan]HARMLESSAI ADMIN LOGIN[/bold cyan]")

    stored_hash = os.getenv("ADMIN_PASSWORD_HASH", "")

    if not stored_hash:
        console.print("[bold red]Admin password is not configured.[/bold red]")
        return False

    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            raise ValueError("Unsupported password hash")

        iterations = int(iterations)

        if not 100000 <= iterations <= 2000000:
            raise ValueError("Invalid iteration count")

        salt_bytes = bytes.fromhex(salt)
        expected_bytes = bytes.fromhex(expected_hash)

    except (ValueError, TypeError):
        console.print("[bold red]Invalid password configuration.[/bold red]")
        return False

    for attempt in range(1, 4):
        password = Prompt.ask(
            f"Administrator password (Attempt {attempt}/3)",
            password=True
        )

        supplied_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            iterations
        )

        if hmac.compare_digest(supplied_hash, expected_bytes):
            console.print(
                "[bold green]Administrator authenticated![/bold green]"
            )
            return True

        console.print("[bold red]Incorrect password![/bold red]")

    console.print(
        "[bold red]Maximum login attempts reached. Access denied.[/bold red]"
    )
    return False
