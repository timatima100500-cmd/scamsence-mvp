"""
voice_analysis/voice_analyzer.py — Голосовой анализатор скамов

Тонкая обёртка над основным ScamAnalyzer:
  1. Принимает транскрипт (текст)
  2. Добавляет голосовой контекст в промпт
  3. Возвращает стандартный AnalysisResponse

Отдельный класс нужен потому что голосовые скамы имеют
специфические паттерны (urgency на слух, robotic phrases,
неестественные переходы) — которые мы подсвечиваем в промпте.
"""
from backend.models.schemas import AnalysisRequest, AnalysisResponse, ContentType


# Специфичные для голоса красные флаги — добавляются в промпт
_VOICE_CONTEXT_PREFIX = """[VOICE TRANSCRIPT ANALYSIS]
This text was transcribed from an audio recording (phone call, voicemail, or video).
Pay special attention to voice-specific scam patterns:
- Artificial urgency delivered verbally ("call us NOW", "don't hang up")
- Impersonation of officials, banks, tech support over the phone
- AI voice cloning indicators: robotic phrasing, unnatural pauses (shown as gaps)
- IRS/Social Security/Microsoft phone scams
- Grandparent scams and family emergency calls
- Vishing (voice phishing) patterns

Transcript:
"""


def analyze_transcript(
    transcript: str,
    source: str = "audio",
    analyzer=None,
) -> AnalysisResponse:
    """
    Анализирует транскрипт на признаки голосового скама.

    Args:
        transcript: текст транскрипции (из Whisper или YouTube)
        source: "audio" | "youtube" — влияет на контекст промпта
        analyzer: экземпляр AnalysisService (инжектируется из FastAPI)

    Returns:
        AnalysisResponse — стандартный ответ анализатора
    """
    from backend.services.analysis_service import get_analysis_service

    service = analyzer or get_analysis_service()

    # Добавляем голосовой контекст перед транскриптом
    source_label = "YouTube video transcript" if source == "youtube" else "audio recording transcript"
    context_prefix = f"[{source_label.upper()}]\n{_VOICE_CONTEXT_PREFIX}"
    enriched_text = context_prefix + transcript

    # Обрезаем до 10000 символов (лимит API)
    if len(enriched_text) > 10000:
        enriched_text = enriched_text[:9900] + "\n...[transcript truncated]"

    request = AnalysisRequest(
        content=enriched_text,
        content_type=ContentType.text,
        language="auto",
    )

    return service.analyze(request)
