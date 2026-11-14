
import os

from dotenv import load_dotenv
from litellm import completion
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# Load API credentials from the local .env file
load_dotenv()


PROVIDERS = {
    "1": {
        "name": "OpenAI",
        "model": "openai/gpt-4o-mini",
        "key": "OPENAI_API_KEY"
    },
    "2": {
        "name": "Anthropic Claude",
        "model": "anthropic/claude-3-5-haiku-latest",
        "key": "ANTHROPIC_API_KEY"
    },
    "3": {
        "name": "Google Gemini",
        "model": "gemini/gemini-2.0-flash",
        "key": "GEMINI_API_KEY"
    }
}


def select_provider():
    console.clear()

    console.print(Panel(
        "[bold cyan]HARMLESSAI — REAL AI MODE[/bold cyan]\n"
        "Connect using your own provider API key.",
        border_style="blue"
    ))

    console.print("1. OpenAI (GPT)")
    console.print("2. Anthropic (Claude)")
    console.print("3. Google (Gemini)")
    console.print("4. Return to main menu")

    choice = Prompt.ask(
        "\nSelect an AI provider",
        choices=["1", "2", "3", "4"]
    )

    if choice == "4":
        return

    provider = PROVIDERS[choice]

    if not os.getenv(provider["key"]):
        console.print(
            f"\n[bold red]Missing API key:[/bold red] {provider['key']}"
        )
        console.print(
            "Add your key to the local .env file and restart HarmlessAI."
        )
        Prompt.ask("\nPress Enter to continue")
        return

    chat_with_provider(provider)


def chat_with_provider(provider):
    console.clear()

    console.print(Panel(
        f"[bold green]Connected mode: {provider['name']}[/bold green]\n"
        "Real API requests may incur charges or use your provider quota.\n"
        "Type 'exit' to return.",
        border_style="green"
    ))

    while True:
        user_prompt = Prompt.ask("\n[bold blue]You[/bold blue]")

        if user_prompt.strip().lower() == "exit":
            break

        if not user_prompt.strip():
            continue

        try:
            response = completion(
                model=provider["model"],
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            answer = response.choices[0].message.content

            console.print(Panel(
                answer or "The provider returned an empty response.",
                title=f"[bold green]{provider['name']} — REAL AI[/bold green]",
                border_style="green"
            ))

        except Exception as error:
            console.print(
                Panel(
                    f"{type(error).__name__}: {error}",
                    title="[bold red]API Request Failed[/bold red]",
                    border_style="red"
                )
            )
