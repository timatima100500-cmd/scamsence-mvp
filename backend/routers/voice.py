"""
backend/routers/voice.py — Voice + YouTube analysis endpoints

POST /api/v1/analyze/youtube  — транскрипт YouTube → ScamAnalyzer
POST /api/v1/analyze/audio    — аудиофайл → Whisper → ScamAnalyzer
GET  /api/v1/voice/status     — проверка доступности Whisper
"""
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from pydantic import BaseModel, Field

from backend.models.schemas import AnalysisResponse
from backend.services.analysis_service import AnalysisService, get_analysis_service
from backend.services.rate_limiter import RateLimiter, get_rate_limiter

router = APIRouter(prefix="/api/v1", tags=["voice"])

# ── Request schemas ───────────────────────────────────────────────────────────

class YouTubeRequest(BaseModel):
    url: str = Field(..., description="YouTube URL или video ID (11 символов)")
    language: str = Field("en", description="Предпочтительный язык транскрипта")

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "language": "en",
            }
        }
    }


# ── Response schemas ──────────────────────────────────────────────────────────

class VoiceAnalysisResponse(AnalysisResponse):
    """Расширение стандартного AnalysisResponse — добавляет поля транскрипции."""
    transcript: str = Field("", description="Полный текст транскрипта")
    transcript_language: str = Field("unknown", description="Язык транскрипта")
    transcript_duration_sec: float = Field(0.0, description="Длительность в секундах")
    video_id: str = Field("", description="YouTube video ID (если применимо)")
    source: str = Field("audio", description="'audio' или 'youtube'")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(request: Request, limiter: RateLimiter) -> None:
    """Единый rate-limit check — бросает HTTPException если лимит исчерпан."""
    ip = _get_client_ip(request)
    rate = limiter.check_and_increment(ip)
    if not rate["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Daily limit reached",
                "message": f"Free plan: {rate['limit']} checks/day. Resets at midnight UTC.",
                "limit": rate["limit"],
                "reset_at": rate["reset_at"],
            },
        )


def _build_response(
    analysis: AnalysisResponse,
    transcript_data: dict,
    source: str,
) -> VoiceAnalysisResponse:
    """Собирает VoiceAnalysisResponse из AnalysisResponse + метаданных транскрипта."""
    return VoiceAnalysisResponse(
        verdict=analysis.verdict,
        probability=analysis.probability,
        red_flags=analysis.red_flags,
        explanation=analysis.explanation,
        recommendations=analysis.recommendations,
        model_used=analysis.model_used,
        analysis_time_ms=analysis.analysis_time_ms,
        similar_cases=analysis.similar_cases,
        transcript=transcript_data.get("text", ""),
        transcript_language=transcript_data.get("language", "unknown"),
        transcript_duration_sec=transcript_data.get("duration_sec", 0.0),
        video_id=transcript_data.get("video_id", ""),
        source=source,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/analyze/youtube",
    response_model=VoiceAnalysisResponse,
    summary="Analyze YouTube video transcript for scam signs",
)
async def analyze_youtube(
    body: YouTubeRequest,
    request: Request,
    service: AnalysisService = Depends(get_analysis_service),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> VoiceAnalysisResponse:
    """
    Получает транскрипт YouTube-видео и анализирует его на признаки скама.
    Не скачивает аудио — использует встроенные субтитры YouTube.
    """
    _check_rate_limit(request, limiter)

    try:
        from voice_analysis.transcriber import transcribe_youtube
        transcript_data = transcribe_youtube(
            body.url,
            preferred_languages=[body.language, "en", "ru"],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка транскрипции: {e}")

    try:
        from voice_analysis.voice_analyzer import analyze_transcript
        analysis = analyze_transcript(
            transcript_data["text"],
            source="youtube",
            analyzer=service,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {e}")

    return _build_response(analysis, transcript_data, source="youtube")


@router.post(
    "/analyze/audio",
    response_model=VoiceAnalysisResponse,
    summary="Transcribe audio file and analyze for scam signs (Pro)",
)
async def analyze_audio(
    request: Request,
    file: UploadFile = File(..., description="Аудиофайл: mp3, wav, m4a, ogg"),
    service: AnalysisService = Depends(get_analysis_service),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> VoiceAnalysisResponse:
    """
    Принимает аудиофайл, транскрибирует через Whisper, анализирует на скам.
    Требует: pip install openai-whisper torch
    """
    _check_rate_limit(request, limiter)

    # Проверяем доступность Whisper до чтения файла
    from voice_analysis.transcriber import AudioTranscriber
    if not AudioTranscriber.is_available():
        raise HTTPException(
            status_code=501,
            detail={
                "error": "Whisper not installed",
                "message": "Voice analysis requires: pip install openai-whisper torch",
                "install_command": "pip install openai-whisper torch",
            },
        )

    # Ограничение размера: 50 МБ
    MAX_SIZE = 50 * 1024 * 1024
    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой: {len(audio_bytes) // 1024 // 1024} МБ. Максимум 50 МБ.",
        )

    try:
        transcript_data = AudioTranscriber.transcribe_bytes(
            audio_bytes,
            filename=file.filename or "audio.wav",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка транскрипции: {e}")

    try:
        from voice_analysis.voice_analyzer import analyze_transcript
        analysis = analyze_transcript(
            transcript_data["text"],
            source="audio",
            analyzer=service,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {e}")

    return _build_response(analysis, transcript_data, source="audio")


@router.get(
    "/voice/status",
    summary="Check voice analysis availability",
)
async def voice_status() -> dict:
    """Проверяет доступность Whisper и youtube-transcript-api."""
    from voice_analysis.transcriber import AudioTranscriber

    whisper_ok = AudioTranscriber.is_available()

    try:
        import youtube_transcript_api  # noqa: F401
        yt_ok = True
        yt_version = getattr(youtube_transcript_api, "__version__", "installed")
    except ImportError:
        yt_ok = False
        yt_version = None

    return {
        "whisper_available": whisper_ok,
        "youtube_transcript_api_available": yt_ok,
        "youtube_transcript_api_version": yt_version,
        "status": "ready" if yt_ok else "partial",
        "notes": {
            "whisper": "pip install openai-whisper torch" if not whisper_ok else "OK",
            "youtube": "pip install youtube-transcript-api" if not yt_ok else "OK",
        },
    }
