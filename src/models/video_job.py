"""VideoJob — mutable state threaded through pipeline stages."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from src.config.settings import Settings


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, limit: int = 48) -> str:
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return s[:limit] or "untitled"


@dataclass
class Script:
    title: str = ""
    body: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class VideoJob:
    topic: str
    index: int
    slug: str
    work_dir: Path
    target_minutes: float = 6.0
    script: Script = field(default_factory=Script)
    voiceover_path: Path | None = None
    video_path: Path | None = None
    thumbnail_path: Path | None = None
    youtube_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def script_path(self) -> Path:
        return self.work_dir / "script.txt"

    @classmethod
    def new(cls, topic: str, index: int, settings: Settings) -> "VideoJob":
        slug = f"{index:02d}-{slugify(topic)}"
        work = settings.cache_dir / "jobs" / slug
        work.mkdir(parents=True, exist_ok=True)
        return cls(topic=topic, index=index, slug=slug, work_dir=work)