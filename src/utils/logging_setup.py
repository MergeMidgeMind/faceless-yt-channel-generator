"""Logging configuration — rich console handler, timestamps, level control."""
from __future__ import annotations

import logging

from rich.logging import RichHandler


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="%H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True, show_path=verbose)],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("moviepy").setLevel(logging.WARNING)