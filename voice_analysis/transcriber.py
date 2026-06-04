"""
voice_analysis/transcriber.py — Audio + YouTube transcription

Two independent modules:
  - transcribe_youtube(url_or_id) → uses youtube-transcript-api (no audio download)
  - AudioTranscriber.transcribe(file_path) → uses OpenAI Whisper (Pro only)

Both return a unified dict: {"text", "language", "duration_sec", ...}
"""
import re
import tempfile
import shutil
from pathlib import Path
from typing import Optional


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_video_id(url_or_id: str) -> str:
    """
    Извлекает 11-символьный video ID из любого формата YouTube-ссылки.
    Поддерживает: watch?v=, youtu.be/, shorts/, embed/, live/
    """
    s = url_or_id.strip()

    # youtu.be/VIDEO_ID
    m = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", s)
    if m:
        return m.group(1)

    # youtube.com/watch?v=VIDEO_ID или &v=VIDEO_ID
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", s)
    if m:
        return m.group(1)

    # youtube.com/shorts/VIDEO_ID, /embed/VIDEO_ID, /live/VIDEO_ID
    m = re.search(r"/(?:shorts|embed|live|v)/([a-zA-Z0-9_-]{11})", s)
    if m:
        return m.group(1)

    # Уже голый ID (ровно 11 символов из допустимого набора)
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", s):
        return s

    raise ValueError(f"Не удалось извлечь video ID из: {url_or_id!r}")


# ── YouTube transcript ────────────────────────────────────────────────────────

def transcribe_youtube(
    url_or_id: str,
    preferred_languages: Optional[list[str]] = None,
) -> dict:
    """
    Получает транскрипт YouTube-видео без скачивания аудио.
    Использует youtube-transcript-api (встроенные субтитры YouTube).

    Args:
        url_or_id: YouTube URL или video ID
        preferred_languages: список языков в порядке предпочтения, напр. ["en", "ru"]

    Returns:
        {
            "text": str,           — полный транскрипт одной строкой
            "video_id": str,
            "language": str,       — фактический язык транскрипта
            "duration_sec": float, — длительность видео в секундах
            "segment_count": int,  — количество сегментов
        }

    Raises:
        RuntimeError: если youtube-transcript-api не установлен или транскрипт недоступен
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise RuntimeError(
            "youtube-transcript-api не установлен. "
            "Запусти: pip install youtube-transcript-api"
        )

    video_id = extract_video_id(url_or_id)
    langs = preferred_languages or ["en", "ru", "de", "fr", "es", "uk", "pl"]

    # v1.x — instance-based API
    api = YouTubeTranscriptApi()
    fetched = None
    detected_language = "auto"

    # Шаг 1: пробуем предпочтительные языки
    try:
        fetched = api.fetch(video_id, languages=langs)
        detected_language = langs[0]
    except Exception:
        pass

    # Шаг 2: берём первый доступный транскрипт из списка
    if fetched is None:
        try:
            transcript_list = api.list(video_id)
            first = next(iter(transcript_list))
            fetched = first.fetch()
            detected_language = getattr(first, "language_code", "auto")
        except Exception as e:
            err = str(e).lower()
            if "disabled" in err or "no transcript" in err or "unavailable" in err:
                raise RuntimeError(
                    f"Транскрипты недоступны для видео {video_id}. "
                    "Автор мог отключить субтитры или видео приватное."
                )
            raise RuntimeError(f"Не удалось получить транскрипт: {e}")

    segments = list(fetched)
    if not segments:
        raise RuntimeError(f"Транскрипт пустой для видео {video_id}")

    # Поддержка обоих форматов: объекты (v1.x) и словари (v0.x)
    def _text(s) -> str:
        return (s.text if hasattr(s, "text") else s.get("text", "")).strip()

    def _start(s) -> float:
        return s.start if hasattr(s, "start") else s.get("start", 0)

    def _dur(s) -> float:
        return s.duration if hasattr(s, "duration") else s.get("duration", 0)

    text = " ".join(_text(s) for s in segments if _text(s))
    last = segments[-1]
    duration = _start(last) + _dur(last)

    return {
        "text": text,
        "video_id": video_id,
        "language": detected_language,
        "duration_sec": round(duration, 1),
        "segment_count": len(segments),
    }


# ── Audio transcription (Whisper) ────────────────────────────────────────────

class AudioTranscriber:
    """
    Транскрибирует аудиофайлы через OpenAI Whisper.
    Загружает модель лениво при первом вызове (~30-90 сек cold start).

    Модели по размеру (точность/скорость):
      tiny  (39M)  — быстро, менее точно
      base  (74M)  — хороший баланс для MVP
      small (244M) — точнее, медленнее
    """

    _SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".webm"}
    _model_cache: dict = {}  # {model_name: model_instance}
    DEFAULT_MODEL = "base"

    @classmethod
    def is_available(cls) -> bool:
        """Возвращает True если openai-whisper установлен."""
        try:
            import whisper  # noqa: F401
            return True
        except ImportError:
            return False

    @classmethod
    def _load_model(cls, model_name: str = DEFAULT_MODEL):
        """
        Загружает модель Whisper (кэш — один раз на процесс).
        Cold start: ~30-90 сек. Повторные вызовы: мгновенно.
        """
        if model_name not in cls._model_cache:
            import whisper
            cls._model_cache[model_name] = whisper.load_model(model_name)
        return cls._model_cache[model_name]

    @classmethod
    def transcribe(
        cls,
        file_path: str | Path,
        model_name: str = DEFAULT_MODEL,
        language: Optional[str] = None,
    ) -> dict:
        """
        Транскрибирует аудиофайл в текст.

        Args:
            file_path: путь к аудиофайлу
            model_name: "tiny", "base", "small", "medium", "large"
            language: принудительный язык (напр. "ru"), или None для auto-detect

        Returns:
            {
                "text": str,
                "language": str,
                "duration_sec": float,
            }

        Raises:
            RuntimeError: Whisper не установлен
            ValueError: неподдерживаемый формат
            FileNotFoundError: файл не найден
        """
        if not cls.is_available():
            raise RuntimeError(
                "openai-whisper не установлен. "
                "Запусти: pip install openai-whisper\n"
                "(Требует PyTorch — ~2 ГБ)"
            )

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Аудиофайл не найден: {path}")

        if path.suffix.lower() not in cls._SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Неподдерживаемый формат: {path.suffix}. "
                f"Поддерживаются: {', '.join(sorted(cls._SUPPORTED_EXTENSIONS))}"
            )

        model = cls._load_model(model_name)

        # fp16=False для совместимости с CPU
        options: dict = {"fp16": False}
        if language:
            options["language"] = language

        result = model.transcribe(str(path), **options)

        text = result.get("text", "").strip()
        if not text:
            raise RuntimeError("Whisper вернул пустую транскрипцию. Проверь аудиофайл.")

        return {
            "text": text,
            "language": result.get("language", "unknown"),
            "duration_sec": round(result.get("duration", 0.0), 1),
        }

    @classmethod
    def transcribe_bytes(
        cls,
        audio_bytes: bytes,
        filename: str,
        model_name: str = DEFAULT_MODEL,
        language: Optional[str] = None,
    ) -> dict:
        """
        Удобная обёртка: сохраняет bytes во временный файл → transcribe().
        Используется для обработки UploadFile из FastAPI.
        """
        suffix = Path(filename).suffix.lower() or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = Path(tmp.name)

        try:
            return cls.transcribe(tmp_path, model_name=model_name, language=language)
        finally:
            tmp_path.unlink(missing_ok=True)
