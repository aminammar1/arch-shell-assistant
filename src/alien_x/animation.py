"""Alien-X inspired loading spinner.

Simple single-line spinner on stderr — no Rich Live / panels,
so it shows in *every* terminal (gnome-terminal, alacritty,
kitty, tmux, VSCode, SSH) and never pollutes piped stdout.

Look: green ``⧗`` hourglass (Omnitrix nod) + braille dial +
rotating lore lines (Bellicus / Serena must agree) + elapsed.

Usage:
    from alien_x.animation import alienx_thinking

    with alienx_thinking():
        answer = call_llm(...)

Notes:
- Writes to stderr so command output on stdout stays clean.
- Non-TTY (pipes/logs): prints one static line, no thread.
- Respects NO_COLOR (no ANSI codes when set).
"""

from __future__ import annotations

import os
import sys
import threading
import time
from contextlib import contextmanager
from typing import IO, Iterator

# Braille dial — readable in basically every monospace font.
DIAL_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# Lore: Alien-X only acts when Bellicus + Serena agree.
# Cycling these makes the wait feel intentional, not frozen.
SPINNER_MESSAGES = [
    "Consulting Bellicus…",
    "Consulting Serena…",
    "Seeking consensus…",
]

_GREEN = "\033[32m"
_BRIGHT_GREEN = "\033[92m"
_RESET = "\033[0m"


def _use_color(stream: IO[str]) -> bool:
    return stream.isatty() and os.environ.get("NO_COLOR") is None


class AlienXLoader:
    """Single-line stderr spinner. Use as context manager."""

    def __init__(
        self,
        base_message: str | None = None,
        stream: IO[str] | None = None,
        interval: float = 0.08,
        # kept for backward compat — ignored (spinner no longer needs Rich)
        console=None,  # noqa: ANN001, ARG002
        refresh_per_second: int | None = None,  # noqa: ARG002
        message: str | None = None,
    ) -> None:
        self.base_message = message or base_message
        self.stream = stream or sys.stderr
        if refresh_per_second:
            interval = 1.0 / refresh_per_second
        self.interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started_at = 0.0
        self._last_len = 0
        self._is_tty = False

    # -- public API -----------------------------------------------------
    def start(self) -> None:
        if self._thread is not None:
            return
        self._started_at = time.monotonic()
        self._is_tty = self.stream.isatty()
        if not self._is_tty:
            # Piped logs: one static line, no thread, no control chars.
            msg = self.base_message or SPINNER_MESSAGES[0]
            self.stream.write(f"⧗ {msg}\n")
            self.stream.flush()
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return  # non-TTY path — nothing to clear
        self._stop.set()
        self._thread.join(timeout=2.0)
        self._thread = None
        # Clear the spinner line.
        try:
            self.stream.write("\r" + " " * self._last_len + "\r")
            self.stream.flush()
        except Exception:
            pass

    def __enter__(self) -> AlienXLoader:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    # -- internals ------------------------------------------------------
    def _spin(self) -> None:
        color = _use_color(self.stream)
        tick = 0
        while not self._stop.is_set():
            dial = DIAL_FRAMES[tick % len(DIAL_FRAMES)]
            if self.base_message:
                msg = self.base_message
            else:
                # new lore line ~every 1.0s
                msg = SPINNER_MESSAGES[(tick // 12) % len(SPINNER_MESSAGES)]
            elapsed = time.monotonic() - self._started_at
            if color:
                line = (
                    f"{_GREEN}{dial}{_RESET} "
                    f"{_BRIGHT_GREEN}⧗{_RESET} {msg} {elapsed:.1f}s"
                )
                # visible length without ANSI codes
                visible = len(f"{dial} ⧗ {msg} {elapsed:.1f}s")
            else:
                line = f"{dial} ⧗ {msg} {elapsed:.1f}s"
                visible = len(line)
            # pad to erase previous longer line
            pad = max(0, self._last_len - visible)
            try:
                self.stream.write("\r" + line + " " * pad)
                self.stream.flush()
            except Exception:
                break
            self._last_len = visible
            tick += 1
            time.sleep(self.interval)


@contextmanager
def alienx_thinking(
    message: str | None = None,
    console=None,  # noqa: ANN001, ARG001 — backward compat
    stream: IO[str] | None = None,
) -> Iterator[AlienXLoader]:
    """Convenience wrapper: ``with alienx_thinking(): ...``."""
    loader = AlienXLoader(base_message=message, stream=stream)
    with loader:
        yield loader


def alienx_intro(console=None, delay: float = 0.0) -> None:  # noqa: ANN001, ARG001
    """No-op, kept for backward compat.

    The old Omnitrix activation flash was removed per user request —
    startup is now just the one-line banner in ``ui.print_intro``.
    """
    return
