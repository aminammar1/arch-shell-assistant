"""CLI entry: one-shot (`alien-x "..."`) + interactive REPL."""

from __future__ import annotations

import sys
from typing import Any

from openai import OpenAI

from alien_x import ui
from alien_x.agent import handle_request
from alien_x.config import load_config
from alien_x.llm import create_client

EXIT_COMMANDS = frozenset({"exit", "quit"})


def run_oneshot(client: OpenAI, model: str, request: str) -> None:
    handle_request(client, model, [], request)


def run_interactive(client: OpenAI, model: str) -> None:
    ui.print_intro()
    history: list[dict[str, Any]] = []
    while True:
        try:
            request = input("alien-x> ").strip()
        except (EOFError, KeyboardInterrupt):
            ui.console.print()
            break
        if not request:
            continue
        if request.lower() in EXIT_COMMANDS:
            break
        handle_request(client, model, history, request)


def main(argv: list[str] | None = None) -> None:
    config = load_config()
    client = create_client(config)
    args = sys.argv[1:] if argv is None else argv
    if args:
        run_oneshot(client, config.model, " ".join(args))
        return
    run_interactive(client, config.model)
