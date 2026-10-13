"""YouTubeClient — OAuth2 + resumable upload against YouTube Data API v3."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from src.config.settings import UploadConfig

log = logging.getLogger("faceless_yt.youtube")

UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    def __init__(self, cfg: UploadConfig) -> None:
        self._cfg = cfg

    def _access_token(self) -> str:
        if not self._cfg.oauth_token_path.exists():
            raise RuntimeError(
                f"missing OAuth token at {self._cfg.oauth_token_path}; run `faceless-yt-auth` once"
            )
        data = json.loads(self._cfg.oauth_token_path.read_text("utf-8"))
        return data["access_token"]

    async def upload(
        self,
        video: Path,
        title: str,
        description: str,
        tags: list[str],
        thumbnail: Path | None,
        privacy: str,
    ) -> str:
        token = self._access_token()
        metadata = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:30],
                "categoryId": self._cfg.category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": self._cfg.made_for_kids,
            },
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        params = {"uploadType": "resumable", "part": "snippet,status"}
        async with httpx.AsyncClient(timeout=None) as client:
            init = await client.post(UPLOAD_URL, params=params, headers=headers, json=metadata)
            init.raise_for_status()
            session_url = init.headers["Location"]
            with video.open("rb") as fh:
                put_headers = {"Content-Type": "video/*", "Content-Length": str(video.stat().st_size)}
                put = await client.put(session_url, headers=put_headers, content=fh.read())
                put.raise_for_status()
                video_id = put.json()["id"]
            if thumbnail and thumbnail.exists():
                await client.post(
                    f"{API_BASE}/thumbnails/set",
                    params={"videoId": video_id},
                    headers={"Authorization": f"Bearer {token}"},
                    files={"image": (thumbnail.name, thumbnail.read_bytes(), "image/png")},
                )
        return video_id