"""Read access keys from the .env file in the project folder (never committed)."""

from __future__ import annotations

import os

from dotenv import dotenv_values

from scripts.util import REPO_ROOT


def load_env() -> dict:
    """Keys from .env, overridden by real environment variables."""
    values = {k: v for k, v in dotenv_values(REPO_ROOT / ".env").items() if v}
    values.update({k: v for k, v in os.environ.items() if v})
    return values
