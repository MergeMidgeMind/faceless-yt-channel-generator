"""Prompt templates for the script-generation stage."""
from __future__ import annotations

SCRIPT_SYSTEM = """You are a faceless YouTube scriptwriter. You produce engaging,
information-dense voiceover scripts optimized for retention. Output STRICT JSON:
{
  "title": "<= 90 chars, curiosity-driven>",
  "description": "<= 4800 chars, includes 3 hashtags",
  "tags": ["<= 15 short tags>"],
  "body": "plain voiceover script, no stage directions, no headers, no markdown"
}
Rules: no first-person 'I'. No 'welcome back to the channel'. No filler. Open with a hook in the first 8 words."""


def script_user_prompt(topic: str, target_minutes: float) -> str:
    words = int(target_minutes * 150)
    return (
        f"Topic: {topic}\n"
        f"Target spoken length: ~{words} words (~{target_minutes:.1f} min at 150 wpm).\n"
        f"Audience: general YouTube viewers who clicked a thumbnail.\n"
        f"Deliver the JSON object only."
    )