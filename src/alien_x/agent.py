"""Agent orchestration: request → clarify → suggest → confirm → run → fix."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from alien_x import ui
from alien_x.config import HISTORY_LIMIT
from alien_x.executor import run_command
from alien_x.llm import build_messages, get_suggestion


def handle_request(
    client: OpenAI, model: str, history: list[dict[str, Any]], request: str
) -> None:
    history.append({"role": "user", "content": request})
    while True:
        suggestion = get_suggestion(client, model, build_messages(history, HISTORY_LIMIT))
        if suggestion is None:
            history.pop()  # drop failed turn so follow-ups stay clean
            return

        if suggestion.is_clarification:
            ui.show_clarification(suggestion.question)
            answer = ui.ask_text("Your answer: ")
            if not answer:
                ui.show_cancelled()
                return
            history.append({"role": "assistant", "content": json.dumps(suggestion.__dict__)})
            history.append({"role": "user", "content": answer})
            continue

        if suggestion.is_refusal:
            ui.show_refusal(suggestion.explanation)
            history.append({"role": "assistant", "content": json.dumps(suggestion.__dict__)})
            return

        ui.show_suggestion(suggestion)
        history.append({"role": "assistant", "content": json.dumps(suggestion.__dict__)})

        if not ui.ask_confirm(suggestion.risk):
            ui.show_cancelled()
            history.append({"role": "user", "content": "Cancelled by user, do not run."})
            return

        code, out = run_command(suggestion.command)
        if code == 0:
            history.append(
                {"role": "user", "content": f"Command succeeded (exit 0): {suggestion.command}"}
            )
            return

        # failure → offer fix, loop to get a new suggestion with full context
        if not ui.ask_fix():
            return
        history.append(
            {
                "role": "user",
                "content": f"That command failed (exit {code}). Output:\n{out}\nFix it.",
            }
        )
