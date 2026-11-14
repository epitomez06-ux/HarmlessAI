
from admin.dashboard import run_admin_dashboard
from admin.remote_dashboard import show_dashboard
from src.folder_monitor import run_folder_monitor
from src.ai_simulator import run_simulation
from src.ai_providers import select_provider

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def show_banner():
    console.clear()

    banner = """
    ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗
    ██║  ██║██╔══██╗██╔══██╗████╗ ████║
    ███████║███████║██╔══██╗██╔████╔██║
    ██╔══██║██╔══██╗██╔══██╗██║╚██╔╝██║
    ██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝

                H A R M L E S S A I
    """

    console.print(Panel(
        banner,
        subtitle="Unlimited AI? Let's see how easy it is to fake.",
        border_style="bright_blue"
    ))


def show_menu():
    table = Table(title="HarmlessAI Main Menu", border_style="blue")

    table.add_column("Option", style="cyan")
    table.add_column("Feature", style="white")
    table.add_column("Status", style="green")

    table.add_row("1", "AI Simulation", "Ready")
    table.add_row("2", "Real AI Providers", "Ready")
    table.add_row("3", "Folder Activity Monitor", "Ready")
    table.add_row("4", "FIM Admin Dashboard", "Ready")
    table.add_row("5", "Remote Admin Dashboard", "Ready")
    table.add_row("6", "Exit", "Ready")

    console.print(table)


def ai_simulation():
    run_simulation()

    console.print(Panel(
        "[bold green]AI SIMULATION MODE[/bold green]\n"
        "This mode generates fictional responses locally.\n"
        "It does not provide real unlimited AI access.",
        border_style="green"
    ))

    console.print("[yellow]Simulated token balance: UNLIMITED[/yellow]")

    Prompt.ask("\nPress Enter to return to the main menu")


def main():
    while True:
        show_banner()
        show_menu()

        choice = Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3", "4", "5", "6"]
        )

        if choice == "1":
            ai_simulation()

        elif choice == "2":
            select_provider()

        elif choice == "3":
            run_folder_monitor()

        elif choice == "4":
            run_admin_dashboard()

        elif choice == "5":
            show_dashboard()

        elif choice == "6":
            console.print(
                "[bold blue]Thank you for using HarmlessAI![/bold blue]"
            )
            break


if __name__ == "__main__":
    main()
