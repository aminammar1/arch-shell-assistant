# arch-shell-assistant

Safe AI agent for Arch Linux: turns plain-language requests into shell
commands, shows them with explanation + risk level, and runs them only
after confirmation.

## Install

From AUR (once published):

```bash
paru -S arch-shell-assistant
# or: yay -S arch-shell-assistant
```

From source:

```bash
makepkg -si
# or for dev: uv tool install .
```

## Setup

Get a free Groq key at https://console.groq.com/keys, then pick **one**:

**A — export (simplest, works everywhere incl. pacman installs):**

```bash
export GROQ_API_KEY="gsk_..."
export GROQ_MODEL="openai/gpt-oss-120b"
```

**B — user config file (persisted):**

```bash
mkdir -p ~/.config/arch-shell-assistant  # legacy path ~/.config/alien-x also works
cp .env.example ~/.config/arch-shell-assistant/.env
# then edit it with your key
```

(Legacy `Groq_API_KEY` / `Groq_Model` spellings are still accepted.
`$XDG_CONFIG_HOME` is respected.)

Config load order (lowest → highest priority):

1. `$XDG_CONFIG_HOME/alien-x/.env` (fallback `~/.config/alien-x/.env`)
2. `./.env` (project-local override, optional)
3. real environment variables (always win)

Pick a model at https://console.groq.com/docs/models
(e.g. `openai/gpt-oss-120b`).

## Run

One-shot:

```bash
arch-shell-assistant "clean up my pacman cache"
# legacy alias still works: alien-x "..."
```

Interactive:

```bash
arch-shell-assistant
# type a request, `exit` to quit
```

Safety: default answer is NO. High-risk commands require typing `yes`.
Nothing runs without confirmation.
