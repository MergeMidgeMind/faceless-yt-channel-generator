"""VideoHandler — assembles B-roll + voiceover + captions into final MP4."""
from __future__ import annotations

import logging

from src.config.settings import Settings
from src.core.registry import register_stage
from src.models.video_job import VideoJob
from src.services.renderer import Renderer

log = logging.getLogger("faceless_yt.handler.video")


@register_stage("render")
class VideoHandler:
    name = "render"

    def __init__(self, settings: Settings) -> None:
        self._renderer = Renderer(settings.render)

    async def handle(self, job: VideoJob, settings: Settings) -> VideoJob:
        if not job.voiceover_path or not job.voiceover_path.exists():
            raise RuntimeError("voiceover missing before render")
        out = job.work_dir / f"{job.slug}.mp4"
        await self._renderer.render(
            voiceover=job.voiceover_path,
            script=job.script.body,
            out=out,
        )
        job.video_path = out
        log.info("rendered: %s", out)
        return job