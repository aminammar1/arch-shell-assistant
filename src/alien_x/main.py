"""Thin entry-point shim (kept for `alien-x = alien_x.main:main`).

All logic lives in `alien_x.cli`, `alien_x.agent`, etc.
"""

from alien_x.cli import main

if __name__ == "__main__":
    main()
