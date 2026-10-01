"""LLM layer: client creation + JSON suggestion parsing.

The Alien-X spinner lives here so every model call
automatically shows it — callers don't need to remember.
"""

from __future__ import annotations

import json
import time
from typing import Any

from openai import OpenAI, OpenAIError

from alien_x.animation import alienx_thinking
from alien_x.config import AlienXConfig
from alien_x.models import Suggestion
from alien_x.prompts import RETRY_JSON_MESSAGE, SYSTEM_PROMPT
from alien_x.ui import console


def create_client(config: AlienXConfig) -> OpenAI:
    return OpenAI(api_key=config.api_key, base_url=config.base_url)


def _raw_chat(
    client: OpenAI, model: str, messages: list[dict[str, Any]]
) -> str | None:
    """One chat call with the Alien-X spinner. Retries once on 429."""
    for attempt in range(2):
        try:
            with alienx_thinking():
                resp = client.chat.completions.create(model=model, messages=messages)
            return ((resp.choices[0].message.content) or "").strip()
        except OpenAIError as e:
            status = getattr(e, "status_code", None)
            msg = str(e)
            is_429 = status == 429 or "429" in msg or "rate" in msg.lower()
            if is_429 and attempt == 0:
                console.print("[yellow]Rate limited (429), retrying once...[/yellow]")
                time.sleep(2)
                continue
            lowered = msg.lower()
            if (
                status == 401
                or "invalid_api_key" in lowered
                or "unauthorized" in lowered
            ):
                console.print(
                    "[red]Invalid API key. Check GROQ_API_KEY "
                    "(export it or ~/.config/arch-shell-assistant/.env).[/red]"
                )
            elif is_429:
                console.print("[red]Rate limit hit. Please wait a bit and try again.[/red]")
            else:
                console.print(f"[red]API error: {msg[:300]}[/red]")
            return None
        except Exception as e:  # network, etc. — never traceback
            console.print(f"[red]Connection error: {str(e)[:200]}[/red]")
            return None
    return None


def _parse_json(raw: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            try:
                data = json.loads(raw[start : end + 1])
                return data if isinstance(data, dict) else None
            except json.JSONDecodeError:
                return None
        return None


def get_suggestion(
    client: OpenAI, model: str, messages: list[dict[str, Any]]
) -> Suggestion | None:
    """Call LLM and return a validated Suggestion. Retries once on bad JSON."""
    current = messages
    for attempt in range(2):
        raw = _raw_chat(client, model, current)
        if raw is None:
            return None
        data = _parse_json(raw)
        if data is not None:
            return Suggestion.from_dict(data)
        if attempt == 0:
            current = current + [{"role": "user", "content": RETRY_JSON_MESSAGE}]
            continue
        console.print("[red]Model returned invalid JSON. Please try again.[/red]")
        return None
    return None


def build_messages(
    history: list[dict[str, Any]], limit: int
) -> list[dict[str, Any]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}] + history[-limit:]
