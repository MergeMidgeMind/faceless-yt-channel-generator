"""Settings loader — TOML on disk, env overrides, pydantic validation."""
from __future__ import annotations

import os
from pathlib import Path

import tomli_w
from pydantic import BaseModel, Field

try:
    import tomllib  # py3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

DEFAULT_CONFIG = Path.home() / ".faceless-yt" / "config.toml"


class TTSConfig(BaseModel):
    engine: str = "edge-tts"
    voice: str = "en-US-GuyNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"


class RenderConfig(BaseModel):
    width: int = 1920
    height: int = 1080
    fps: int = 30
    broll_dir: Path = Path("assets/broll")
    music_dir: Path = Path("assets/music")
    burn_captions: bool = True


class UploadConfig(BaseModel):
    enabled: bool = False
    privacy: str = Field(default="unlisted", pattern="^(public|unlisted|private)$")
    category_id: str = "22"
    made_for_kids: bool = False
    oauth_token_path: Path = Path(".cache/youtube_token.json")


class LLMConfig(BaseModel):
    provider: str = "openai-compatible"
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    api_key_env: str = "FACELESS_YT_API_KEY"
    temperature: float = 0.8
    max_tokens: int = 900


class Settings(BaseModel):
    llm: LLMConfig = LLMConfig()
    tts: TTSConfig = TTSConfig()
    render: RenderConfig = RenderConfig()
    upload: UploadConfig = UploadConfig()
    output_dir: Path = Path("outputs")
    cache_dir: Path = Path(".cache")


def load_settings(path: Path | None = None) -> Settings:
    cfg_path = path or DEFAULT_CONFIG
    if cfg_path.exists():
        raw = tomllib.loads(cfg_path.read_text("utf-8"))
    else:
        raw = {}
    # env overrides — FACELESS_YT_LLM__MODEL=... style
    for key, val in os.environ.items():
        if not key.startswith("FACELESS_YT_"):
            continue
        parts = key[len("FACELESS_YT_"):].lower().split("__")
        node = raw
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = val
    return Settings.model_validate(raw)


def dump_default(path: Path | None = None) -> Path:
    target = path or DEFAULT_CONFIG
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(tomli_w.dumps(Settings().model_dump(mode="json")))
    return target