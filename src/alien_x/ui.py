"""Terminal UI: console singleton + all rendering / prompts.

Nothing here talks to the LLM or runs shell commands — it only
displays things and reads user confirmations.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from alien_x.models import RISK_COLORS, Suggestion

console = Console()


def print_intro() -> None:
    """Startup banner (no animation — just one line)."""
    console.print("[bold]alien-x[/bold] — type a request, `exit` to quit.")


def show_suggestion(s: Suggestion) -> None:
    color = RISK_COLORS.get(s.risk, "white")
    body = (
        f"[bold cyan]$ {s.command}[/bold cyan]\n\n"
        f"{s.explanation}\n\n"
        f"Risk: [{color}]{s.risk}[/{color}]"
    )
    if s.needs_root:
        body += "  •  needs root (sudo)"
    console.print(Panel(body, title="◈ alien-x", border_style="green", expand=False))


def show_clarification(question: str) -> None:
    console.print(f"[yellow]Need clarification:[/yellow] {question}")


def show_refusal(explanation: str) -> None:
    console.print(f"[red]Refused:[/red] {explanation}")


def show_cancelled() -> None:
    console.print("[dim]Cancelled — nothing was run.[/dim]")


def _safe_input(prompt: str) -> str | None:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        console.print()
        return None


def ask_confirm(risk: str) -> bool:
    """Default is NO. High-risk requires typing `yes` exactly."""
    if risk == "high":
        console.print("[red]High risk — type 'yes' exactly to confirm.[/red]")
        answer = _safe_input("Type 'yes' to run: ")
        return answer is not None and answer.strip() == "yes"
    answer = _safe_input("Run it? [y/N] ")
    if answer is None:
        return False
    return answer.strip().lower() in ("y", "yes")


def ask_text(prompt: str) -> str | None:
    """Generic input helper. Returns None on EOF/Ctrl-C."""
    raw = _safe_input(prompt)
    return None if raw is None else raw.strip()


def ask_fix() -> bool:
    answer = _safe_input("Command failed. Ask model for a fix? [y/N] ")
    if answer is None:
        return False
    return answer.strip().lower() in ("y", "yes")
