"""ScriptHandler — LLM-driven script generation for a faceless video."""
from __future__ import annotations

import logging

from src.config.settings import Settings
from src.core.registry import register_stage
from src.models.video_job import VideoJob
from src.services.llm_client import LLMClient
from src.utils.prompt_templates import SCRIPT_SYSTEM, script_user_prompt
from src.utils.text_clean import normalize_script

log = logging.getLogger("faceless_yt.handler.script")


@register_stage("script")
class ScriptHandler:
    name = "script"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm = LLMClient(settings.llm)

    async def handle(self, job: VideoJob, settings: Settings) -> VideoJob:
        user = script_user_prompt(topic=job.topic, target_minutes=job.target_minutes)
        raw = await self._llm.complete(system=SCRIPT_SYSTEM, user=user)
        job.script = normalize_script(raw)
        job.title = job.script.title or job.topic.title()
        job.description = job.script.description
        job.tags = job.script.tags
        job.script_path.write_text(job.script.body, encoding="utf-8")
        log.info("script written: %d chars -> %s", len(job.script.body), job.script_path)
        return job