"""
frontend/pages/text_check.py — Страница проверки текста / email / объявлений

Универсальная проверка любого текстового контента.
Поддерживает: SMS, сообщения, email-тексты, объявления, телефонные скрипты.
"""
import streamlit as st
import requests
from frontend.components.result_card import render_result_card


# URL бэкенда (читается из session_state или дефолт)
_API_URL = "http://127.0.0.1:8000/api/v1/analyze"

# Примеры для быстрого тестирования
_EXAMPLES = {
    "— Select example —": "",
    "🚨 Crypto scam (EN)": "URGENT: Your account has been suspended! Send bitcoin to restore access immediately or lose all your funds forever.",
    "🚨 IRS impersonation": "IRS FINAL NOTICE: You owe $3,420 in back taxes. A warrant for your arrest has been issued. Call 1-888-XXX-XXXX within 1 hour and pay via gift cards.",
    "🚨 Prize scam": "Congratulations! You have been selected as our lucky winner. You won a brand new iPhone 15 Pro! Provide your credit card for the $2 shipping fee.",
    "⚠️ Pig butchering": "Hi! I accidentally texted the wrong number. You seem interesting, want to chat? I work in finance and make great returns on crypto. I can show you how.",
    "✅ Legit (order)": "Your Amazon order #123-456 has shipped. Track your package at amazon.com/orders. Delivery expected June 5.",
    "✅ Legit (appointment)": "Reminder: your dentist appointment is scheduled for June 10 at 10:30 AM. Call (555) 123-4567 to reschedule.",
}


def render() -> None:
    """Главная функция страницы — вызывается из main.py."""

    st.title("🔍 Text / Message Check")
    st.markdown(
        "Paste any suspicious text — SMS, email, ad, chat message, phone script — "
        "and ScamSence will analyze it for fraud patterns."
    )

    # ── Быстрые примеры ──────────────────────────────────────────────────────
    selected_example = st.selectbox("Quick examples", options=list(_EXAMPLES.keys()))
    example_text = _EXAMPLES[selected_example]

    # ── Текст для анализа ────────────────────────────────────────────────────
    content = st.text_area(
        "Paste text here",
        value=example_text,
        height=180,
        max_chars=50000,
        placeholder="Paste the suspicious message, email, ad, or script here...",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        content_type = st.selectbox(
            "Content type",
            options=["text", "email", "url"],
            format_func=lambda x: {"text": "💬 Text / Message", "email": "📧 Email", "url": "🔗 URL"}[x],
        )
    with col2:
        language = st.selectbox(
            "Language",
            options=["auto", "en", "ru"],
            format_func=lambda x: {"auto": "🌐 Auto-detect", "en": "🇬🇧 English", "ru": "🇷🇺 Russian"}[x],
        )

    # ── Кнопка анализа ───────────────────────────────────────────────────────
    analyze_clicked = st.button(
        "🔍 Analyze",
        type="primary",
        disabled=len(content.strip()) < 10,
        use_container_width=True,
    )

    if len(content.strip()) > 0 and len(content.strip()) < 10:
        st.caption("⚠️ Text too short (minimum 10 characters)")

    # ── Анализ ───────────────────────────────────────────────────────────────
    if analyze_clicked and len(content.strip()) >= 10:
        with st.spinner("Analyzing..."):
            result = _call_api(content.strip(), content_type, language)

        if result:
            st.markdown("---")
            st.markdown("## Analysis Result")
            render_result_card(result)

            # Сохраняем в историю
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.insert(0, {
                "text": content[:80] + ("..." if len(content) > 80 else ""),
                "verdict": result.get("verdict", "Unknown"),
                "probability": result.get("probability", 0),
                "content_type": content_type,
            })
            # Максимум 20 в истории
            st.session_state.history = st.session_state.history[:20]


def _call_api(content: str, content_type: str, language: str) -> dict | None:
    """
    Вызывает FastAPI backend для анализа.
    Показывает понятное сообщение об ошибке если API недоступен.
    """
    try:
        response = requests.post(
            _API_URL,
            json={"content": content, "content_type": content_type, "language": language},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot connect to ScamSence API. "
            "Make sure the backend is running:\n\n"
            "```\nuvicorn backend.app:app --reload\n```"
        )
        return None

    except requests.exceptions.Timeout:
        st.error("⏱️ Analysis timed out. Try a shorter text.")
        return None

    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.status_code} — {e.response.text[:200]}")
        return None

    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None
