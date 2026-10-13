"""Text normalization for LLM output — JSON extraction, script cleanup."""
from __future__ import annotations

import json
import re
from typing import Any

from src.models.video_job import Script

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)
_WHITESPACE = re.compile(r"[ \t]+")
_MULTI_NL = re.compile(r"\n{3,}")