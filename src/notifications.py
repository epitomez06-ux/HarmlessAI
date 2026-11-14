
from rich.console import Console
from rich.panel import Panel

console = Console()


def monitoring_started(folder):
    console.print(
        Panel(
            f"[bold green]FOLDER MONITORING STARTED[/bold green]\n\n"
            f"Selected folder:\n{folder}\n\n"
            "Monitoring status: ACTIVE",
            border_style="green"
        )
    )


def monitoring_stopped():
    console.print(
        Panel(
            "[bold yellow]FOLDER MONITORING STOPPED[/bold yellow]\n\n"
            "Activity monitoring has ended.",
            border_style="yellow"
        )
    )


def activity_notification(action, path):
    console.print(
        f"[bold cyan]ACTIVITY ALERT:[/bold cyan] {action}\n"
        f"[dim]{path}[/dim]"
    )
