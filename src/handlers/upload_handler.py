"""UploadHandler — pushes finished video + metadata to YouTube Data API v3."""
from __future__ import annotations

import logging

from src.config.settings import Settings
from src.core.registry import register_stage
from src.models.video_job import VideoJob
from src.services.youtube_client import YouTubeClient

log = logging.getLogger("faceless_yt.handler.upload")


@register_stage("upload")
class UploadHandler:
    name = "upload"

    def __init__(self, settings: Settings) -> None:
        self._yt = YouTubeClient(settings.upload)

    async def handle(self, job: VideoJob, settings: Settings) -> VideoJob:
        if not settings.upload.enabled:
            log.info("upload disabled — skipping")
            return job
        if not job.video_path:
            raise RuntimeError("no video to upload")
        video_id = await self._yt.upload(
            video=job.video_path,
            title=job.title,
            description=job.description,
            tags=job.tags,
            thumbnail=job.thumbnail_path,
            privacy=settings.upload.privacy,
        )
        job.youtube_id = video_id
        log.info("uploaded: https://youtu.be/%s", video_id)
        return job