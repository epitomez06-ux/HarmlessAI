
import csv
from pathlib import Path
from collections import Counter

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from src.authentication import verify_admin

console = Console()

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "logs" / "activity.log"
EXPORT_FILE = PROJECT_DIR / "logs" / "activity_report.csv"


def read_activity():
    events = []

    if not LOG_FILE.exists():
        return events

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line.startswith("[") or "] " not in line:
                continue

            try:
                timestamp, details = line.split("] ", 1)
                parts = details.split(" | ", 2)

                if len(parts) != 3:
                    continue

                action, item_type, path = parts

                events.append({
                    "timestamp": timestamp.strip("[]"),
                    "action": action,
                    "type": item_type,
                    "path": path
                })

            except ValueError:
                continue

    return events


def export_csv(events):
    with EXPORT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["timestamp", "action", "type", "path"]
        )

        writer.writeheader()
        writer.writerows(events)

    console.print(f"[green]Report exported to: {EXPORT_FILE}[/green]")


def show_dashboard():
    events = read_activity()

    console.clear()

    console.print(Panel(
        "[bold cyan]HARMLESSAI — ADMIN FIM DASHBOARD[/bold cyan]\n"
        "[green]Administrator authenticated[/green]",
        border_style="blue"
    ))

    actions = Counter(event["action"] for event in events)

    table = Table(title="File Activity Statistics")

    table.add_column("Activity", style="cyan")
    table.add_column("Count", style="green", justify="right")

    table.add_row("Created", str(actions["CREATED"]))
    table.add_row("Modified", str(actions["MODIFIED"]))
    table.add_row("Deleted", str(actions["DELETED"]))
    table.add_row("Renamed / Moved", str(actions["RENAMED/MOVED"]))
    table.add_row("Total Events", str(len(events)))

    console.print(table)

    history = Table(title="Recent Activity")

    history.add_column("Timestamp", style="cyan")
    history.add_column("Action", style="yellow")
    history.add_column("Type", style="green")
    history.add_column("Path", style="white", overflow="fold")

    for event in events[-15:]:
        history.add_row(
            event["timestamp"],
            event["action"],
            event["type"],
            event["path"]
        )

    console.print(history)

    console.print("\n1. Export activity report to CSV")
    console.print("2. Refresh dashboard")
    console.print("3. Return to main menu")

    choice = Prompt.ask(
        "Select an option",
        choices=["1", "2", "3"]
    )

    if choice == "1":
        export_csv(events)
        Prompt.ask("Press Enter to continue")
        show_dashboard()

    elif choice == "2":
        show_dashboard()


def run_admin_dashboard():
    console.clear()

    if not verify_admin():
        Prompt.ask("Press Enter to return to the main menu")
        return

    show_dashboard()
