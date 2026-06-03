"""
core/prompts.py — Промпты для LLM-анализа скамов

Используются в День 8 когда подключим Ollama / Claude.
Сейчас нужны как reference — MockLLM их не вызывает.
"""

# ── System prompt ─────────────────────────────────────────────────────────────

SCAM_ANALYSIS_SYSTEM_PROMPT = """You are ScamSence, an expert fraud detection AI trained on thousands of real scam cases from 2020-2026.

Your job: analyze the provided content (text, email, or URL) and determine the probability of fraud.

Current scam landscape (2026):
- AI voice cloning scams are widespread — fake family emergency calls
- Pig butchering: long romance/friendship warmup, then crypto investment
- Professional fake English: grammatically correct but templated
- QR code phishing replacing traditional URL scams
- Deepfake video calls from "bank managers"

You MUST respond in this exact format:
---
VERDICT: [Scam | Likely Scam | Suspicious | Legitimate]
PROBABILITY: [0-100]
RED_FLAGS:
- [pattern_type]: [description] (severity: N/10)
EXPLANATION: [2-3 sentences]
RECOMMENDATIONS:
- [actionable advice]
---

Be decisive. Avoid "could be" language when evidence is clear."""


# ── User prompt builders ──────────────────────────────────────────────────────

def build_text_prompt(content: str, pre_detected_patterns: list[str] | None = None) -> str:
    """Промпт для анализа текстового сообщения."""
    pattern_hint = ""
    if pre_detected_patterns:
        # Подсказываем LLM что уже нашёл keyword-анализатор — экономит токены
        pattern_hint = f"\nPre-detected patterns: {', '.join(pre_detected_patterns)}\n"

    return f"""Analyze this message for fraud indicators:{pattern_hint}

MESSAGE:
{content}

Content type: text message / SMS"""


def build_email_prompt(content: str, pre_detected_patterns: list[str] | None = None) -> str:
    """Промпт для анализа email."""
    pattern_hint = ""
    if pre_detected_patterns:
        pattern_hint = f"\nPre-detected patterns: {', '.join(pre_detected_patterns)}\n"

    return f"""Analyze this email for fraud indicators:{pattern_hint}

EMAIL CONTENT:
{content}

Pay special attention to: sender impersonation, urgency language, suspicious links, attachment warnings."""


def build_url_prompt(url: str, pre_detected_patterns: list[str] | None = None) -> str:
    """Промпт для анализа URL."""
    pattern_hint = ""
    if pre_detected_patterns:
        pattern_hint = f"\nPre-detected patterns: {', '.join(pre_detected_patterns)}\n"

    return f"""Analyze this URL for fraud indicators:{pattern_hint}

URL: {url}

Check for: typosquatting, URL shorteners, suspicious TLDs, lookalike domains, path manipulation."""


def build_prompt(content: str, content_type: str,
                 pre_detected_patterns: list[str] | None = None) -> str:
    """Роутер промптов — выбирает нужный по content_type."""
    builders = {
        "email": build_email_prompt,
        "url": build_url_prompt,
    }
    builder = builders.get(content_type, build_text_prompt)
    return builder(content, pre_detected_patterns)
