"""Shell execution: stream live output, capture tail for self-fix."""

from __future__ import annotations

import subprocess

from alien_x.ui import console

TAIL_LIMIT = 4000  # chars of combined output kept for the fix-up prompt


def run_command(cmd: str) -> tuple[int, str]:
    """Run via shell, stream stdout+stderr live. Returns (exit_code, tail)."""
    console.print(f"[dim]Running: {cmd}[/dim]")
    output: list[str] = []
    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        console.print(f"[red]Failed to start command: {e}[/red]")
        return 1, str(e)

    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            print(line, end="", flush=True)
            output.append(line)
    except KeyboardInterrupt:
        proc.terminate()
        console.print("\n[yellow]Interrupted.[/yellow]")
    proc.wait()
    code = proc.returncode
    console.print(f"[bold]Exit code: {code}[/bold]")
    return code, "".join(output)[-TAIL_LIMIT:]
