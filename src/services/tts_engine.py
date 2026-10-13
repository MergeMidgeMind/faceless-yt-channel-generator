"""TTSEngine — edge-tts wrapper. Emits MP3 at 24kHz mono."""
from __future__ import annotations

import logging
from pathlib import Path

import edge_tts

from src.config.settings import TTSConfig

log = logging.getLogger("faceless_yt.tts")


class TTSEngine:
    def __init__(self, cfg: TTSConfig) -> None:
        self._cfg = cfg

    async def synthesize(self, text: str, out: Path) -> Path:
        out.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(
            text=text,
            voice=self._cfg.voice,
            rate=self._cfg.rate,
            pitch=self._cfg.pitch,
        )
        with out.open("wb") as fh:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    fh.write(chunk["data"])
        return out