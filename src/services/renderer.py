"""Renderer — MoviePy composition of voiceover + b-roll + captions."""
from __future__ import annotations

import logging
import random
from pathlib import Path

from moviepy.editor import (  # type: ignore[import-untyped]
    AudioFileClip, CompositeVideoClip, ImageClip, TextClip, VideoFileClip, concatenate_videoclips,
)

from src.config.settings import RenderConfig

log = logging.getLogger("faceless_yt.render")


class Renderer:
    def __init__(self, cfg: RenderConfig) -> None:
        self._cfg = cfg

    def _pick_broll(self) -> list[Path]:
        pool = [p for p in self._cfg.broll_dir.glob("*.mp4")] if self._cfg.broll_dir.exists() else []
        if not pool:
            raise FileNotFoundError(f"no b-roll under {self._cfg.broll_dir}")
        random.shuffle(pool)
        return pool

    async def render(self, voiceover: Path, script: str, out: Path) -> Path:
        audio = AudioFileClip(str(voiceover))
        duration = audio.duration
        clips = []
        pool = self._pick_broll()
        cursor = 0.0
        idx = 0
        while cursor < duration:
            seg = VideoFileClip(str(pool[idx % len(pool)])).subclip(0, min(8.0, duration - cursor))
            seg = seg.resize(newsize=(self._cfg.width, self._cfg.height)).set_start(cursor)
            clips.append(seg)
            cursor += seg.duration
            idx += 1
        base = concatenate_videoclips(clips, method="compose").set_duration(duration)
        layers = [base]
        if self._cfg.burn_captions:
            cap = (
                TextClip(script[:120], fontsize=48, color="white", stroke_color="black", stroke_width=2)
                .set_position(("center", self._cfg.height - 140))
                .set_duration(duration)
            )
            layers.append(cap)
        final = CompositeVideoClip(layers).set_audio(audio)
        out.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(str(out), fps=self._cfg.fps, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        return out