
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.notifications import (
    monitoring_started,
    monitoring_stopped,
    activity_notification
)

from src.remote_client import send_activity

console = Console()

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "logs" / "activity.log"


class FolderActivityHandler(FileSystemEventHandler):

    def record_event(self, action, path, destination=None, is_directory=False):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item_type = "Folder" if is_directory else "File"

        message = (
            f"[{timestamp}] {action} | "
            f"{item_type} | {path}"
        )

        remote_path = str(path)

        if destination:
            message += f" -> {destination}"
            remote_path += f" -> {destination}"

        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(message + "\n")

        console.print(f"[cyan]{message}[/cyan]")
        activity_notification(action, path)

        # Forward activity metadata to the LAN server.
        send_activity(action, item_type, remote_path)

    def on_created(self, event):
        self.record_event(
            "CREATED",
            event.src_path,
            is_directory=event.is_directory
        )

    def on_modified(self, event):
        if not event.is_directory:
            self.record_event("MODIFIED", event.src_path)

    def on_deleted(self, event):
        self.record_event(
            "DELETED",
            event.src_path,
            is_directory=event.is_directory
        )

    def on_moved(self, event):
        self.record_event(
            "RENAMED/MOVED",
            event.src_path,
            event.dest_path,
            event.is_directory
        )


def run_folder_monitor():
    console.clear()

    console.print(Panel(
        "[bold green]HARMLESSAI — FOLDER ACTIVITY MONITOR[/bold green]\n"
        "Monitoring is visible and limited to your selected folder.",
        border_style="green"
    ))

    folder = Prompt.ask(
        "Enter the full folder path to monitor"
    ).strip().strip('"')

    selected_folder = Path(folder).expanduser()

    if not selected_folder.is_dir():
        console.print("[bold red]Invalid folder path![/bold red]")
        Prompt.ask("Press Enter to return")
        return

    selected_folder = selected_folder.resolve()

    observer = Observer()
    handler = FolderActivityHandler()

    try:
        observer.schedule(
            handler,
            str(selected_folder),
            recursive=True
        )

        observer.start()

        monitoring_started(selected_folder)

        console.print(Panel(
            f"[bold green]MONITORING: ACTIVE[/bold green]\n"
            f"Folder: {selected_folder}\n"
            "Subfolders: Included\n"
            "Local log: logs/activity.log\n"
            "Remote server: Enabled\n\n"
            "Monitoring is active and visible.\n"
            "Type STOP to end monitoring.",
            border_style="green"
        ))

        while True:
            command = Prompt.ask("[bold yellow]Monitor[/bold yellow]")

            if command.strip().lower() == "stop":
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Stop requested.[/yellow]")

    finally:
        if observer.is_alive():
            observer.stop()
            observer.join()

        monitoring_stopped()

        Prompt.ask("Press Enter to return to the main menu")
