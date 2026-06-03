"""
frontend/pages/email_check.py - Email Check page

Fields: sender, subject, body, optional raw headers.
Composes full email text -> POST /api/v1/analyze (content_type=email).
"""
import streamlit as st
import requests
import json

from frontend.components.result_card import render_result_card

API_URL = "http://127.0.0.1:8000/api/v1/analyze"

_EXAMPLES = {
    "Sberbank - account blocked": {
        "sender": "security@sberbank-support-alert.ru",
        "subject": "СРОЧНО: Ваш аккаунт заблокирован",
        "body": (
            "Уважаемый клиент!\n\n"
            "Ваш аккаунт Сбербанк Онлайн заблокирован из-за подозрительной активности.\n\n"
            "Для восстановления доступа СРОЧНО перейдите: http://sberbank-secure-login.xyz/verify\n\n"
            "Если не сделаете этого в течение 24 часов — аккаунт заблокируют навсегда.\n\n"
            "С уважением,\nСлужба безопасности Сбербанк"
        ),
        "headers": "From: security@sberbank-support-alert.ru\nReply-To: noreply@gmail.com",
    },
    "Apple iPhone prize lottery": {
        "sender": "winners@apple-promo-giveaway.com",
        "subject": "Congratulations! You won Apple iPhone 15 Pro — Claim Now!",
        "body": (
            "Dear Lucky Winner!\n\n"
            "You have been randomly selected to receive an Apple iPhone 15 Pro.\n"
            "To claim your prize, pay a small shipping fee of $4.99.\n\n"
            "IMPORTANT: This offer expires in 48 hours.\n"
            "Claim here: http://bit.ly/apple-winner-claim-2026"
        ),
        "headers": "",
    },
    "Microsoft tech support scam": {
        "sender": "support@microsoft-helpdesk-team.info",
        "subject": "Critical: Your Windows License Has Expired",
        "body": (
            "Dear Microsoft Customer,\n\n"
            "Your Windows 11 license has expired and your PC is at risk.\n\n"
            "To restore access:\n"
            "1. Call: +1-800-555-0199\n"
            "2. Visit: http://ms-support-helpdesk.xyz/fix\n\n"
            "DO NOT RESTART your computer.\n\nMicrosoft Security Team"
        ),
        "headers": "X-Originating-IP: 185.234.219.45",
    },
    "Crypto investment guaranteed 300%": {
        "sender": "invest@crypto-profit-guarantee.io",
        "subject": "Эксклюзивное: 300% прибыли за 30 дней",
        "body": (
            "Привет!\n\n"
            "Наша команда зарабатывает 300% в месяц на крипто-рынке.\n"
            "Открываем доступ для 10 новых инвесторов.\n"
            "Минимум $500 BTC/USDT. Выплата через 30 дней: $1500 гарантировано!\n\n"
            "Telegram: @crypto_guru_pro\n\nАлексей Волков, Senior Analyst"
        ),
        "headers": "",
    },
}

_RED_FLAGS = [
    ("📧 Домен отправителя", "sberbank-support-alert.ru вместо sberbank.ru"),
    ("↩️ Reply-To подмена", "Reply-To ведёт на другой адрес чем From"),
    ("⏰ Срочность", "«24 часа», «немедленно», «сейчас»"),
    ("🔗 Подозрительный URL", "Домен не совпадает с заявленной организацией"),
    ("🎁 Слишком хорошо", "Выигрыши, призы, гарантированная прибыль"),
    ("📞 Требование звонка", "Просят звонить на левый номер"),
]


def _build_email_text(sender: str, subject: str, body: str, headers: str) -> str:
    """
    Собирает полный email-текст для анализатора.
    Структурируем явно чтобы модель правильно классифицировала контекст.
    """
    parts = []
    if headers.strip():
        parts.append(f"[EMAIL HEADERS]\n{headers.strip()}")
    if sender.strip():
        parts.append(f"From: {sender.strip()}")
    if subject.strip():
        parts.append(f"Subject: {subject.strip()}")
    if body.strip():
        parts.append(f"\n[EMAIL BODY]\n{body.strip()}")
    return "\n".join(parts)


def _call_api(content: str) -> dict | None:
    """Отправляет email-текст в API, возвращает результат или None."""
    try:
        resp = requests.post(API_URL, json={"content": content, "content_type": "email"}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API недоступен. Запусти: `uvicorn backend.app:app --reload`")
    except requests.exceptions.Timeout:
        st.error("⏱️ API не ответил за 30 секунд.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP {e}")
    except json.JSONDecodeError:
        st.error("❌ Некорректный ответ от API.")
    return None


def render() -> None:
    """Renders the Email Check page."""
    st.markdown("## 📧 Email Check")
    st.markdown(
        "Вставь содержимое подозрительного письма — анализируем отправителя, "
        "тему, ссылки и паттерны давления."
    )
    st.markdown("---")

    # Example loader
    col_ex, col_load = st.columns([3, 1])
    with col_ex:
        example_key = st.selectbox(
            "Загрузить пример",
            options=["— выбери пример —"] + list(_EXAMPLES.keys()),
            key="email_example_select",
        )
    with col_load:
        st.markdown("<br>", unsafe_allow_html=True)
        load_clicked = st.button("Загрузить", key="load_email_example", use_container_width=True)

    # Init session state fields
    for k, v in [("es_sender", ""), ("es_subject", ""), ("es_body", ""), ("es_headers", "")]:
        if k not in st.session_state:
            st.session_state[k] = v

    if load_clicked and example_key != "— выбери пример —":
        ex = _EXAMPLES[example_key]
        st.session_state.es_sender = ex["sender"]
        st.session_state.es_subject = ex["subject"]
        st.session_state.es_body = ex["body"]
        st.session_state.es_headers = ex["headers"]
        st.rerun()

    st.markdown("---")

    col_meta, col_body_col = st.columns([1, 1.6])

    with col_meta:
        st.markdown("#### Метаданные письма")
        sender = st.text_input("📤 От кого (From)", value=st.session_state.es_sender,
                               placeholder="security@bank-alert.xyz", key="es_sender_input")
        subject = st.text_input("📌 Тема (Subject)", value=st.session_state.es_subject,
                                placeholder="СРОЧНО: Ваш аккаунт заблокирован", key="es_subject_input")

        with st.expander("⚙️ Технические заголовки (опционально)"):
            headers_val = st.text_area(
                "Raw headers", value=st.session_state.es_headers, height=100,
                placeholder="From: ...\nReply-To: ...\nX-Originating-IP: ...",
                key="es_headers_input",
                help="Скопируй из «Показать оригинал» в почтовом клиенте",
            )

        with st.expander("🔴 На что обращать внимание"):
            for flag, example in _RED_FLAGS:
                st.markdown(f"**{flag}** — *{example}*")

    with col_body_col:
        st.markdown("#### Текст письма")
        body = st.text_area(
            "Тело письма", value=st.session_state.es_body, height=340,
            placeholder="Вставь полный текст письма...",
            key="es_body_input", label_visibility="collapsed",
        )

    st.markdown("---")
    col_l, col_c, col_r = st.columns([2, 1.5, 2])
    with col_c:
        analyze = st.button("🔍 Проверить Email", type="primary",
                            use_container_width=True, key="analyze_email_btn")

    if analyze:
        full_text = _build_email_text(sender, subject, body, headers_val)
        if len(full_text.strip()) < 20:
            st.warning("⚠️ Введи хотя бы адрес отправителя и тему письма.")
        else:
            with st.spinner("Анализируем email..."):
                result = _call_api(full_text)
            if result:
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.insert(0, {
                    "text": f"[EMAIL] {subject or sender}",
                    "verdict": result.get("verdict", "Unknown"),
                    "probability": result.get("scam_probability", 0),
                    "content_type": "email",
                })
                st.markdown("---")
                render_result_card(result)
                verdict = result.get("verdict", "")
                if verdict in ("Scam", "Likely Scam"):
                    st.error(
                        "📧 **Email-совет:** Не переходи по ссылкам. "
                        "Свяжись с организацией напрямую через официальный сайт. Пометь как спам."
                    )
                elif verdict == "Suspicious":
                    st.warning(
                        "📧 **Email-совет:** Проверь домен отправителя вручную. "
                        "Не отвечай и не кликай ссылки до выяснения."
                    )
