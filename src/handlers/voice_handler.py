"""VoiceHandler — TTS synthesis to WAV/MP3 via edge-tts (or pluggable engine)."""
from __future__ import annotations

import logging
from pathlib import Path

from src.config.settings import Settings
from src.core.registry import register_stage
from src.models.video_job import VideoJob
from src.services.tts_engine import TTSEngine

log = logging.getLogger("faceless_yt.handler.voice")


@register_stage("voice")
class VoiceHandler:
    name = "voice"

    def __init__(self, settings: Settings) -> None:
        self._engine = TTSEngine(settings.tts)

    async def handle(self, job: VideoJob, settings: Settings) -> VideoJob:
        out: Path = job.work_dir / "voiceover.mp3"
        await self._engine.synthesize(job.script.body, out)
        job.voiceover_path = out
        log.info("voiceover: %s (%.1f KB)", out, out.stat().st_size / 1024)
        return job