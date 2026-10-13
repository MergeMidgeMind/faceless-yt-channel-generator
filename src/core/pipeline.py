"""ChannelPipeline — staged async orchestrator for faceless video production."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from src.config.settings import Settings
from src.models.video_job import VideoJob

log = logging.getLogger("faceless_yt.pipeline")


class Stage(Protocol):
    name: str

    async def handle(self, job: VideoJob, settings: Settings) -> VideoJob: ...


@dataclass
class PipelineResult:
    produced: list[Path] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)


class ChannelPipeline:
    """Runs registered stages sequentially per job. Stages mutate VideoJob in place."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._stages: list[Stage] = []
        self.on_log: Callable[[str], None] | None = None

    def register(self, stage: Stage) -> None:
        self._stages.append(stage)

    def _emit(self, msg: str) -> None:
        log.info(msg)
        if self.on_log:
            self.on_log(msg)

    async def _run_one(self, topic: str, index: int, dry_run: bool) -> Path | None:
        job = VideoJob.new(topic=topic, index=index, settings=self.settings)
        self._emit(f"[job {index}] start topic={topic!r} slug={job.slug}")
        for stage in self._stages:
            if dry_run and stage.name == "upload":
                self._emit(f"[job {index}] skip {stage.name} (dry-run)")
                continue
            self._emit(f"[job {index}] stage={stage.name}")
            try:
                job = await asyncio.wait_for(stage.handle(job, self.settings), timeout=stage_timeout(stage))
            except asyncio.TimeoutError:
                self._emit(f"[job {index}] stage={stage.name} TIMEOUT")
                return None
            except Exception as exc:  # noqa: BLE001
                self._emit(f"[job {index}] stage={stage.name} FAILED: {exc}")
                return None
        return job.video_path

    async def run(self, topic: str, count: int = 1, dry_run: bool = False) -> int:
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)
        self.settings.cache_dir.mkdir(parents=True, exist_ok=True)
        results = await asyncio.gather(
            *(self._run_one(topic, i + 1, dry_run) for i in range(count)),
            return_exceptions=False,
        )
        ok = [p for p in results if p is not None]
        self._emit(f"[pipeline] produced {len(ok)}/{count}")
        return 0 if len(ok) == count else 1


def stage_timeout(stage: Stage) -> float:
    # generous defaults; long stages (render, upload) get more room
    return {"render": 900.0, "upload": 300.0}.get(stage.name, 120.0)