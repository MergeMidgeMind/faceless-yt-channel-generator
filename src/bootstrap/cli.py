"""Headless CLI entrypoint. Wires services and dispatches to handlers."""
from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from src.config.settings import load_settings
from src.core.pipeline import ChannelPipeline
from src.handlers.script_handler import ScriptHandler
from src.handlers.voice_handler import VoiceHandler
from src.handlers.video_handler import VideoHandler
from src.handlers.upload_handler import UploadHandler
from src.utils.logging_setup import configure_logging

log = logging.getLogger("faceless_yt.cli")


def _build_pipeline(cfg_path: Path | None) -> ChannelPipeline:
    settings = load_settings(cfg_path)
    pipeline = ChannelPipeline(settings)
    pipeline.register(ScriptHandler(settings))
    pipeline.register(VoiceHandler(settings))
    pipeline.register(VideoHandler(settings))
    pipeline.register(UploadHandler(settings))
    return pipeline


def main() -> int:
    parser = argparse.ArgumentParser(prog="faceless-yt", description="Faceless YouTube channel generator")
    parser.add_argument("--config", type=Path, default=None, help="Path to config TOML")
    parser.add_argument("--topic", required=True, help="Video topic seed")
    parser.add_argument("--count", type=int, default=1, help="Number of videos to produce")
    parser.add_argument("--dry-run", action="store_true", help="Skip upload stage")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    configure_logging(verbose=args.verbose)
    pipeline = _build_pipeline(args.config)
    rc = asyncio.run(pipeline.run(topic=args.topic, count=args.count, dry_run=args.dry_run))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())