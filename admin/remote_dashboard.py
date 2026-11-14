
import sqlite3
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from src.authentication import verify_admin

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_DIR / "data" / "remote_activity.db"

console = Console()


def load_remote_activity():
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute("""
            SELECT device_name, action, item_type, path, timestamp
            FROM activity
            ORDER BY id DESC
            LIMIT 50
        """).fetchall()


def show_dashboard():
    if not verify_admin():
        return

    while True:
        console.clear()

        events = load_remote_activity()

        console.print(Panel(
            "[bold green]HARMLESSAI — REMOTE ADMIN DASHBOARD[/bold green]\n"
            "Remote device activity received by this server",
            border_style="green"
        ))

        table = Table(title="Recent Remote Activity")

        table.add_column("Device", style="cyan")
        table.add_column("Action", style="yellow")
        table.add_column("Type")
        table.add_column("Path")
        table.add_column("Timestamp", style="dim")

        for device, action, item_type, path, timestamp in events:
            table.add_row(
                device,
                action,
                item_type,
                path,
                timestamp
            )

        console.print(table)

        console.print("\n[1] Refresh dashboard")
        console.print("[2] Return to main menu")

        choice = Prompt.ask("Select an option", choices=["1", "2"])

        if choice == "2":
            break
