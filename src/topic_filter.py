from __future__ import annotations

import re
from pathlib import Path


AI_PRIMARY_PATTERNS = [
    r"\b(llm|large language model|reasoning model|reasoning ai|inference|agentic ai|ai agent)\b",
    r"\b(text-to-image|image generation|image model|diffusion|text-to-video|video generation|music generation|ai music|suno|udio|runway|kling|luma)\b",
    r"\b(openai|anthropic|gemini|claude|deepseek|llama|mistral|hugging ?face|copilot|midjourney|stability ai)\b",
    r"\b(ai tool|ai platform|model update|model release|ai launch|artificial intelligence|machine learning)\b",
]

OFF_TOPIC_PATTERNS = [
    r"\b(bra|bras|lingerie|fashion)\b",
    r"\b(murder|mass shooting|crime|homicide|police blotter)\b",
    r"\b(surveillance|panopticon|public safety camera|cta blue line)\b",
    r"\b(peptides?|religion|pope|homilies?)\b",
    r"\b(robot|robots|robotic|robotics|humanoid|drone)\b",
]

AI_CONTEXT_PATTERNS = [
    r"\b(ai|artificial intelligence|machine learning|model|llm|reasoning|generative|generator)\b",
]


def _text_blob(*parts: str) -> str:
    return " ".join([(p or "") for p in parts]).lower()


def is_ai_topic(title: str, summary: str = "", content: str = "") -> bool:
    text = _text_blob(title, summary, content)

    has_ai_primary = any(re.search(p, text, flags=re.IGNORECASE) for p in AI_PRIMARY_PATTERNS)
    if not has_ai_primary:
        return False

    off_topic_hit = any(re.search(p, text, flags=re.IGNORECASE) for p in OFF_TOPIC_PATTERNS)
    has_ai_context = any(re.search(p, text, flags=re.IGNORECASE) for p in AI_CONTEXT_PATTERNS)

    if off_topic_hit and not has_ai_context:
        return False

    if "surveillance" in text and not has_ai_primary:
        return False

    return True


def is_ai_topic_strict(title: str, summary: str = "", content: str = "") -> bool:
    """Single strict classifier used across generation, site rendering, and X posting."""
    text = _text_blob(title, summary, content)

    has_ai_primary = any(re.search(p, text, flags=re.IGNORECASE) for p in AI_PRIMARY_PATTERNS)
    if not has_ai_primary:
        return False

    off_topic_hit = any(re.search(p, text, flags=re.IGNORECASE) for p in OFF_TOPIC_PATTERNS)
    if off_topic_hit:
        return False

    return True


def briefing_is_ai(md_path: Path, *, strict: bool = True) -> bool:
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    title = ""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            title = s[2:].strip()
            break

    if strict:
        return is_ai_topic_strict(title=title, content=text)
    return is_ai_topic(title=title, content=text)
