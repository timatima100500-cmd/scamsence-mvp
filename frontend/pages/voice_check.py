"""
frontend/pages/voice_check.py — Voice & YouTube Scam Detector

Two tabs:
  🎬 YouTube — paste URL → fetch transcript → AI verdict
  🎙️ Audio  — upload MP3/WAV → Whisper → AI verdict (Pro)
"""
import streamlit as st
import requests
import json

from frontend.components.result_card import render_result_card

API_BASE = "http://127.0.0.1:8000/api/v1"

# ── Example YouTube URLs for testing ─────────────────────────────────────────
_YT_EXAMPLES = {
    "🏛️ IRS tax scam robocall": "https://www.youtube.com/watch?v=Ii6nTITZOlI",
    "👨‍💻 Microsoft tech support scam call": "https://www.youtube.com/watch?v=eg2o-DjGKxk",
    "💰 Crypto investment pitch": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
}


# ── API calls ─────────────────────────────────────────────────────────────────

def _analyze_youtube(url: str) -> dict | None:
    """POST /api/v1/analyze/youtube"""
    try:
        resp = requests.post(
            f"{API_BASE}/analyze/youtube",
            json={"url": url, "language": "en"},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start: `uvicorn backend.app:app --reload`")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out after 60s.")
    except requests.exceptions.HTTPError as e:
        _handle_http_error(e)
    except json.JSONDecodeError:
        st.error("❌ Invalid API response.")
    return None


def _analyze_audio(file_bytes: bytes, filename: str) -> dict | None:
    """POST /api/v1/analyze/audio — multipart form upload"""
    try:
        resp = requests.post(
            f"{API_BASE}/analyze/audio",
            files={"file": (filename, file_bytes, _mime(filename))},
            timeout=300,  # Whisper может работать долго
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start: `uvicorn backend.app:app --reload`")
    except requests.exceptions.Timeout:
        st.error("⏱️ Transcription timed out (300s). Try a shorter clip.")
    except requests.exceptions.HTTPError as e:
        _handle_http_error(e)
    except json.JSONDecodeError:
        st.error("❌ Invalid API response.")
    return None


def _check_voice_status() -> dict:
    """GET /api/v1/voice/status"""
    try:
        resp = requests.get(f"{API_BASE}/voice/status", timeout=5)
        return resp.json()
    except Exception:
        return {"whisper_available": False, "youtube_transcript_api_available": False}


def _handle_http_error(e: requests.exceptions.HTTPError) -> None:
    if e.response is None:
        st.error(f"❌ HTTP error: {e}")
        return
    code = e.response.status_code
    try:
        detail = e.response.json().get("detail", str(e))
    except Exception:
        detail = str(e)

    if code == 429:
        st.error("🚫 Daily limit reached. Resets at midnight UTC.")
    elif code == 422:
        st.error(f"⚠️ {detail}")
    elif code == 501:
        if isinstance(detail, dict):
            st.warning(
                f"🔧 **Whisper not installed.** "
                f"Run: `{detail.get('install_command', 'pip install openai-whisper torch')}`"
            )
        else:
            st.warning(f"🔧 {detail}")
    elif code == 413:
        st.error(f"📦 File too large. {detail}")
    else:
        st.error(f"❌ HTTP {code}: {detail}")


def _mime(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "mp3": "audio/mpeg", "wav": "audio/wav",
        "m4a": "audio/mp4", "ogg": "audio/ogg",
        "flac": "audio/flac",
    }.get(ext, "audio/mpeg")


# ── Result display ────────────────────────────────────────────────────────────

def _show_transcript(result: dict) -> None:
    """Показывает транскрипт в сворачиваемом блоке с метаданными."""
    transcript = result.get("transcript", "")
    lang = result.get("transcript_language", "?")
    dur = result.get("transcript_duration_sec", 0)
    video_id = result.get("video_id", "")
    source = result.get("source", "audio")

    if not transcript:
        return

    # Метаданные
    meta_parts = []
    if dur:
        minutes = int(dur // 60)
        seconds = int(dur % 60)
        meta_parts.append(f"⏱ {minutes}:{seconds:02d}")
    if lang and lang != "unknown":
        meta_parts.append(f"🌐 {lang.upper()}")
    meta_parts.append(f"📝 {len(transcript.split())} words")
    if video_id and source == "youtube":
        meta_parts.append(f"▶️ [youtube.com/watch?v={video_id}](https://youtube.com/watch?v={video_id})")

    meta_str = " · ".join(meta_parts)

    with st.expander(f"📄 Transcript — {meta_str}", expanded=False):
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);'
            f'border-radius:8px;padding:16px;font-size:0.85rem;line-height:1.7;'
            f'color:#7a8fa8;max-height:300px;overflow-y:auto;">{transcript}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"{len(transcript)} characters")


def _save_to_history(result: dict, label: str) -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {
        "text": label,
        "verdict": result.get("verdict", "Unknown"),
        "probability": result.get("probability", 0),
        "content_type": "voice",
    })


# ── Tab: YouTube ──────────────────────────────────────────────────────────────

def _render_youtube_tab(yt_available: bool) -> None:
    st.markdown("### 🎬 YouTube Video Analysis")
    st.markdown(
        "Paste a YouTube URL — we fetch the built-in transcript and check for scam patterns. "
        "**No audio download required.**"
    )

    if not yt_available:
        st.warning(
            "⚠️ `youtube-transcript-api` not installed on the backend.  \n"
            "Run: `pip install youtube-transcript-api` then restart uvicorn."
        )

    st.markdown("---")

    # Example loader
    col_ex, col_load = st.columns([3, 1])
    with col_ex:
        example_choice = st.selectbox(
            "Load an example URL",
            options=["— paste your own URL below —"] + list(_YT_EXAMPLES.keys()),
            key="yt_example_select",
        )
    with col_load:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Load", key="yt_load_btn", use_container_width=True):
            if example_choice != "— paste your own URL below —":
                st.session_state.yt_url = _YT_EXAMPLES[example_choice]
                st.rerun()

    if "yt_url" not in st.session_state:
        st.session_state.yt_url = ""

    url_input = st.text_input(
        "YouTube URL or video ID",
        value=st.session_state.yt_url,
        placeholder="https://www.youtube.com/watch?v=...",
        key="yt_url_input",
    )

    # Tips
    with st.expander("ℹ️ Tips — when transcripts are available"):
        st.markdown(
            "- Most public videos have auto-generated captions ✅\n"
            "- Shorts and livestreams may lack transcripts ⚠️\n"
            "- Private/unlisted videos: no access ❌\n"
            "- Videos shorter than ~30 seconds may have no captions ❌\n"
            "- Best results: phone scam recordings, investment pitch videos"
        )

    st.markdown("---")

    col_l, col_btn, col_r = st.columns([1.5, 2, 1.5])
    with col_btn:
        analyze_yt = st.button(
            "🔍 Analyze YouTube Video",
            type="primary",
            use_container_width=True,
            key="yt_analyze_btn",
        )

    if analyze_yt:
        url = url_input.strip()
        if not url:
            st.warning("⚠️ Paste a YouTube URL first.")
        else:
            with st.spinner("Fetching transcript and analyzing..."):
                result = _analyze_youtube(url)
            if result:
                transcript = result.get("transcript", "")
                video_id = result.get("video_id", url)
                _save_to_history(result, f"[YT] {video_id}")
                st.markdown("---")
                _show_transcript(result)
                render_result_card(result)
                verdict = result.get("verdict", "")
                if verdict in ("Scam", "Likely Scam"):
                    st.error(
                        "🎬 **Warning:** This video contains scam patterns. "
                        "Do NOT follow any instructions, call any numbers, or send money."
                    )


# ── Tab: Audio ────────────────────────────────────────────────────────────────

def _render_audio_tab(whisper_available: bool) -> None:
    st.markdown("### 🎙️ Audio File Analysis")

    if not whisper_available:
        st.markdown(
            '<div style="background:rgba(0,148,212,0.07);border:1px solid rgba(0,148,212,0.22);'
            'border-radius:10px;padding:16px 20px;margin-bottom:16px;">'
            '<div style="font-size:0.75rem;font-weight:700;color:#00b8f0;text-transform:uppercase;'
            'letter-spacing:0.08em;margin-bottom:8px;">⚙️ Setup Required</div>'
            '<div style="font-size:0.88rem;color:#7a8fa8;line-height:1.7;">'
            'Audio transcription requires <b style="color:#e8f0ff;">OpenAI Whisper</b>.<br>'
            'Install it in your Python environment (requires PyTorch ~2 GB):<br>'
            '<code style="background:rgba(255,255,255,0.06);padding:2px 8px;border-radius:4px;'
            'color:#00b8f0;">pip install openai-whisper torch</code>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        "Upload a phone call recording, voicemail, or audio from a suspicious video. "
        "AI transcribes it and checks for scam patterns."
    )
    st.markdown(
        '<span style="display:inline-block;background:linear-gradient(135deg,#0094d4,#005f8a);'
        'color:#fff;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:100px;">'
        '⭐ PRO FEATURE</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    # What we detect
    with st.expander("🔍 What we detect in voice recordings"):
        st.markdown(
            "- **IRS / Social Security scams** — fake government officials\n"
            "- **Bank fraud calls** — impersonating your bank\n"
            "- **Tech support scams** — fake Microsoft / Apple calls\n"
            "- **Grandparent scams** — family emergency + money request\n"
            "- **Vishing** (voice phishing) — urgency + personal info request\n"
            "- **AI voice cloning** — robotic phrasing, unnatural speech patterns"
        )

    st.markdown("---")

    uploaded_audio = st.file_uploader(
        "Upload audio file",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        key="audio_upload",
        help="Max 50 MB. Supported: MP3, WAV, M4A, OGG, FLAC",
        disabled=not whisper_available,
    )

    if uploaded_audio:
        size_mb = len(uploaded_audio.getvalue()) / 1024 / 1024
        st.info(f"📎 **{uploaded_audio.name}** · {size_mb:.1f} MB")

    st.markdown("---")

    col_l, col_btn, col_r = st.columns([1.5, 2, 1.5])
    with col_btn:
        analyze_audio = st.button(
            "🎙️ Transcribe & Analyze",
            type="primary",
            use_container_width=True,
            key="audio_analyze_btn",
            disabled=uploaded_audio is None,  # только если файл не загружен
        )

    if analyze_audio and uploaded_audio:
        audio_bytes = uploaded_audio.getvalue()
        with st.spinner("Transcribing with Whisper… this may take 30-90 seconds."):
            result = _analyze_audio(audio_bytes, uploaded_audio.name)
        if result:
            _save_to_history(result, f"[AUDIO] {uploaded_audio.name}")
            st.markdown("---")
            _show_transcript(result)
            render_result_card(result)
            verdict = result.get("verdict", "")
            if verdict in ("Scam", "Likely Scam"):
                st.error(
                    "🎙️ **Warning:** This recording shows scam patterns. "
                    "Do NOT call back any numbers mentioned or provide personal information."
                )


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    """Renders the Voice & YouTube Check page."""
    st.markdown(
        "<h2 style='color:#e8f0ff;margin-bottom:4px;'>🎙️ Voice & Video Analysis</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#7a8fa8;margin-bottom:0;'>"
        "Analyze YouTube videos and audio recordings for scam patterns.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Check backend status
    status = _check_voice_status()
    yt_available = status.get("youtube_transcript_api_available", False)
    whisper_available = status.get("whisper_available", False)

    # Status bar
    yt_icon = "✅" if yt_available else "❌"
    wh_icon = "✅" if whisper_available else "❌"
    st.markdown(
        f'<div style="display:flex;gap:20px;margin-bottom:8px;">'
        f'<span style="font-size:0.75rem;color:#3a4a5c;">{yt_icon} YouTube transcript</span>'
        f'<span style="font-size:0.75rem;color:#3a4a5c;">{wh_icon} Whisper (audio)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    tab_yt, tab_audio = st.tabs(["🎬 YouTube", "🎙️ Audio (Pro)"])

    with tab_yt:
        _render_youtube_tab(yt_available)

    with tab_audio:
        _render_audio_tab(whisper_available)
