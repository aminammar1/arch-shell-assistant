"""Configuration loading.

Works the same whether installed via `uv tool`, `pipx`, or pacman:

1. ``$XDG_CONFIG_HOME/alien-x/.env`` (fallback: ``~/.config/alien-x/.env``)
2. ``./.env`` (project-local override, optional)
3. real environment variables (highest priority — always win)

Pacman users can therefore pick either style:

    # style A — export (no files)
    export GROQ_API_KEY="gsk_..."
    export GROQ_MODEL="openai/gpt-oss-120b"

    # style B — user config file
    mkdir -p ~/.config/alien-x
    printf 'GROQ_API_KEY=gsk_...\\nGROQ_MODEL=openai/gpt-oss-120b\\n' \\
      > ~/.config/alien-x/.env

Legacy ``Groq_API_KEY`` / ``Groq_Model`` spellings are still accepted.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

BASE_URL = "https://api.groq.com/openai/v1"
HISTORY_LIMIT = 10  # max messages (excluding system) sent to the LLM

APP_DIR_NAME = "arch-shell-assistant"
LEGACY_DIR_NAME = "alien-x"  # pre-rename path, still honored
DOTENV_NAME = ".env"


def _base_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    return Path(xdg).expanduser() if xdg else Path.home() / ".config"


def config_file_path() -> Path:
    """User config file, respecting XDG_CONFIG_HOME."""
    return _base_config_dir() / APP_DIR_NAME / DOTENV_NAME


def legacy_config_file_path() -> Path:
    """Pre-rename location, still read for backward compat."""
    return _base_config_dir() / LEGACY_DIR_NAME / DOTENV_NAME


def _first_present(*names: str, mapping: dict[str, str]) -> str:
    for name in names:
        value = mapping.get(name, "").strip()
        if value:
            return value
    return ""


@dataclass(frozen=True)
class AlienXConfig:
    api_key: str
    model: str
    base_url: str = BASE_URL


def load_dotenv_files(extra: Path | None = None) -> dict[str, str]:
    """Read config files (no env). Useful for tests / debugging."""
    merged: dict[str, str] = {}
    paths = [config_file_path(), legacy_config_file_path(), Path.cwd() / DOTENV_NAME]
    if extra is not None:
        paths.append(extra)
    for path in paths:
        if path.is_file():
            for key, value in dotenv_values(path).items():
                if value is not None:
                    merged[key] = value
    return merged


def load_config() -> AlienXConfig:
    """Read files + env. Exits with a helpful message if incomplete."""
    # late import to avoid circular dependency (ui must not import config)
    from alien_x.ui import console

    merged = load_dotenv_files()
    env = dict(os.environ)

    api_key = _first_present("GROQ_API_KEY", "Groq_API_KEY", mapping=env) or _first_present(
        "GROQ_API_KEY", "Groq_API_KEY", mapping=merged
    )
    model = _first_present("GROQ_MODEL", "Groq_Model", mapping=env) or _first_present(
        "GROQ_MODEL", "Groq_Model", mapping=merged
    )
    base_url = (
        _first_present("GROQ_BASE_URL", "Groq_BASE_URL", mapping=env)
        or _first_present("GROQ_BASE_URL", "Groq_BASE_URL", mapping=merged)
        or BASE_URL
    )

    cfg_path = config_file_path()
    if not api_key:
        console.print(
            "[red]Missing GROQ_API_KEY.[/red]\n"
            "Get a free key at https://console.groq.com/keys\n"
            "then either export it:\n"
            '  export GROQ_API_KEY="gsk_..."\n'
            '  export GROQ_MODEL="openai/gpt-oss-120b"\n'
            "or put it in your user config:\n"
            f"  mkdir -p {cfg_path.parent}\n"
            f"  printf 'GROQ_API_KEY=gsk_...\\nGROQ_MODEL=openai/gpt-oss-120b\\n' > {cfg_path}\n"
            "(Legacy Groq_API_KEY / Groq_Model spellings and ~/.config/alien-x/.env also work.)"
        )
        sys.exit(1)
    if not model:
        console.print(
            "[red]Missing GROQ_MODEL.[/red]\n"
            "Pick a model at https://console.groq.com/docs/models\n"
            "then either export it:\n"
            '  export GROQ_MODEL="openai/gpt-oss-120b"\n'
            "or set it in your user config or ./.env:\n"
            '  GROQ_MODEL=openai/gpt-oss-120b'
        )
        sys.exit(1)
    return AlienXConfig(api_key=api_key, model=model, base_url=base_url)
