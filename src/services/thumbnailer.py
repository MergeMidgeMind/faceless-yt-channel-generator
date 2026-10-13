"""Thumbnailer — 1280x720 title card composited over a b-roll frame."""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip  # type: ignore[import-untyped]

from src.config.settings import RenderConfig

log = logging.getLogger("faceless_yt.thumb")

THUMB_SIZE = (1280, 720)


class Thumbnailer:
    def __init__(self, cfg: RenderConfig) -> None:
        self._cfg = cfg

    def _grab_frame(self, video: Path | None) -> Image.Image:
        if video and video.exists():
            clip = VideoFileClip(str(video))
            frame = clip.get_frame(min(1.0, clip.duration / 2))
            clip.close()
            return Image.fromarray(frame).resize(THUMB_SIZE)
        return Image.new("RGB", THUMB_SIZE, (18, 18, 24))

    async def compose(self, title: str, source_video: Path | None, out: Path) -> Path:
        base = self._grab_frame(source_video)
        draw = ImageDraw.Draw(base, "RGBA")
        draw.rectangle([(0, THUMB_SIZE[1] - 220), (THUMB_SIZE[0], THUMB_SIZE[1])], fill=(0, 0, 0, 160))
        try:
            font = ImageFont.truetype("arialbd.ttf", 88)
        except OSError:
            font = ImageFont.load_default()
        draw.text((60, THUMB_SIZE[1] - 190), title[:42], font=font, fill=(255, 255, 255))
        out.parent.mkdir(parents=True, exist_ok=True)
        base.save(out, "PNG")
        return out