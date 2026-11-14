
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()



def generate_response(prompt):
    question = prompt.lower().strip()
    words = question.split()

    if "python" in question:
        return (
            "Python is a high-level programming language known for "
            "its simple syntax and readability. It is commonly used "
            "for automation, web development, data analysis, and AI."
        )

    elif "philippines" in question or "phillpines" in question:
        return (
            "The Philippines is an archipelago in Southeast Asia. "
            "Its capital is Manila. It is known for its beautiful "
            "islands, diverse culture, and rich history. "
            "This is a simulated educational response."
        )

    elif "artificial intelligence" in question or " ai " in f" {question} ":
        return (
            "Artificial Intelligence (AI) is technology that allows "
            "computer systems to perform tasks that normally require "
            "human intelligence, such as recognizing patterns and "
            "understanding language."
        )

    elif "programming tips" in question or "coding tips" in question:
        return (
            "Here are three programming tips:\n\n"
            "1. Write clean and readable code.\n"
            "2. Break large problems into smaller tasks.\n"
            "3. Test your code regularly."
        )

    elif "game" in question or "gaming" in question:
        return (
            "Game development combines programming, design, "
            "sound, and creativity. Start with a small project "
            "and gradually add more features."
        )

    elif any(word in words for word in ["hello", "hi", "hey"]):
        return (
            "Hello! Welcome to HarmlessAI. "
            "What would you like to explore today?"
        )

    else:
        return (
            "That's an interesting question! This is a simulated "
            "response. The demonstration engine does not understand "
            "every question yet."
        )

def run_simulation():
    console.clear()

    console.print(Panel(
        "[bold green]HARMLESSAI — SIMULATION MODE[/bold green]\n"
        "[yellow]Demonstration only: responses are fictional.[/yellow]",
        border_style="green"
    ))

    console.print("[bold cyan]Simulated token balance: UNLIMITED[/bold cyan]")
    console.print("[dim]Type 'exit' to return to the main menu.[/dim]\n")

    while True:
        user_prompt = Prompt.ask("[bold blue]You[/bold blue]")

        if user_prompt.lower().strip() == "exit":
            break

        if not user_prompt.strip():
            continue

        response = generate_response(user_prompt)

        console.print(Panel(
            response,
            title="[bold green]HarmlessAI (SIMULATED)[/bold green]",
            border_style="green"
        ))

        console.print("[yellow]Simulated token balance: UNLIMITED[/yellow]\n")
