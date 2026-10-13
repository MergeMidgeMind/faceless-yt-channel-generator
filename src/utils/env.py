"""Env helpers — dotenv load + required key lookup."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_api_key(env_name: str) -> str:
    val = os.environ.get(env_name, "").strip()
    if not val:
        raise RuntimeError(f"missing API key in env var {env_name!r}; add it to .env")
    return val