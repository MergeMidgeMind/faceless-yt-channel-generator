"""ThumbnailHandler — composes a 1280x720 thumbnail from title + b-roll frame."""
from __future__ import annotations

import logging

from src.config.settings import Settings
from src.core.registry import register_stage
from src.models.video_job import VideoJob
from src.services.thumbnailer import Thumbnailer

log = logging.getLogger("faceless_yt.handler.thumbnail")


@register_stage("thumbnail")
class ThumbnailHandler:
    name = "thumbnail"

    def __init__(self, settings: Settings) -> None:
        self._thumb = Thumbnailer(settings.render)

    async def handle(self, job: VideoJob, settings: Settings) -> VideoJob:
        out = job.work_dir / "thumbnail.png"
        await self._thumb.compose(title=job.title, source_video=job.video_path, out=out)
        job.thumbnail_path = out
        log.info("thumbnail: %s", out)
        return job