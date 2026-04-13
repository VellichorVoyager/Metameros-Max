"""Configuration management for Gradient ADK.

The Model Access Key can be injected in two ways (highest priority first):

1. Environment variable  ``GRADIENT_API_KEY``  — set this in your shell or
   deployment environment before running any gradient command.

2. Config file  ``~/.gradient/config.json``  — written by
   ``gradient agent configure --api-key <KEY>``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR: Path = Path.home() / ".gradient"
CONFIG_FILE: Path = CONFIG_DIR / "config.json"

# ------------------------------------------------------------------
# Environment variable used to inject the Model Access Key
# ------------------------------------------------------------------
ENV_API_KEY = "GRADIENT_API_KEY"

DEFAULT_API_BASE = "https://api.gradient.digitalocean.com/v1"


def load_config() -> dict[str, Any]:
    """Return the config dict from disk, or an empty dict if absent."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict[str, Any]) -> None:
    """Persist *config* to the config file, creating directories as needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_api_key(config: dict[str, Any] | None = None) -> str | None:
    """Return the Model Access Key from the environment or the config file.

    The environment variable ``GRADIENT_API_KEY`` always takes precedence.
    """
    key = os.environ.get(ENV_API_KEY)
    if key:
        return key
    if config is None:
        config = load_config()
    return config.get("api_key") or None
