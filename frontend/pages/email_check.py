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
    "🏦 Bank phishing (Sberbank)": {
        "sender": "security@sberbank-support-alert.ru",
        "subject": "URGENT: Your account has been blocked",
        "body": (
            "Dear Customer,\n\n"
            "Your Sberbank Online account has been blocked due to suspicious activity.\n\n"
            "To restore access, URGENTLY follow this link: http://sberbank-secure-login.xyz/verify\n\n"
            "If you do not do this within 24 hours, your account will be permanently blocked.\n\n"
            "Sincerely,\nSberbank Security Service"
        ),
        "headers": "From: security@sberbank-support-alert.ru\nReply-To: noreply@gmail.com",
    },
    "🎰 Apple prize lottery": {
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
    "👨‍💻 Microsoft tech support scam": {
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
    "🐷 Crypto investment 300% guaranteed": {
        "sender": "invest@crypto-profit-guarantee.io",
        "subject": "Exclusive: 300% profit in 30 days — guaranteed",
        "body": (
            "Hi!\n\n"
            "Our team earns 300% per month on the crypto market.\n"
            "We are opening access for 10 new investors.\n"
            "Minimum $500 BTC/USDT. Payout in 30 days: $1500 guaranteed!\n\n"
            "Telegram: @crypto_guru_pro\n\nAlex Volkov, Senior Analyst"
        ),
        "headers": "",
    },
}

_RED_FLAGS = [
    ("📧 Sender domain", "sberbank-support-alert.ru instead of sberbank.ru"),
    ("↩️ Reply-To spoofing", "Reply-To points to a different address than From"),
    ("⏰ Urgency pressure", "\"24 hours\", \"immediately\", \"act now\""),
    ("🔗 Suspicious URL", "Domain doesn't match the claimed organization"),
    ("🎁 Too good to be true", "Prizes, winnings, guaranteed returns"),
    ("📞 Fake phone number", "Asking you to call an unofficial number"),
]


def _build_email_text(sender: str, subject: str, body: str, headers: str) -> str:
    """
    Assembles full email text for the analyzer.
    Structured explicitly so the model correctly classifies context.
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
    """Sends email text to API, returns result dict or None on error."""
    try:
        resp = requests.post(API_URL, json={"content": content, "content_type": "email"}, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start it: `uvicorn backend.app:app --reload`")
    except requests.exceptions.Timeout:
        st.error("⏱️ API did not respond in 120 seconds.")
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            st.error("🚫 Daily limit reached. Resets at midnight UTC.")
        else:
            st.error(f"❌ HTTP error: {e}")
    except json.JSONDecodeError:
        st.error("❌ Invalid response from API.")
    return None


def render() -> None:
    """Renders the Email Check page."""
    st.markdown("## 📧 Email Check")
    st.markdown(
        "Paste the contents of a suspicious email — we analyze the sender, "
        "subject, links, and pressure patterns."
    )
    st.markdown("---")

    # Example selector (Load button is at the bottom row)
    example_key = st.selectbox(
        "Load an example",
        options=["— choose example —"] + list(_EXAMPLES.keys()),
        key="email_example_select",
    )

    # Init session state fields
    for k, v in [("es_sender", ""), ("es_subject", ""), ("es_body", ""), ("es_headers", "")]:
        if k not in st.session_state:
            st.session_state[k] = v

    st.markdown("---")

    col_meta, col_body_col = st.columns([1, 1.6])

    with col_meta:
        st.markdown("#### Email metadata")
        sender = st.text_input(
            "📤 From (sender)",
            value=st.session_state.es_sender,
            placeholder="security@bank-alert.xyz",
            key="es_sender_input",
        )
        subject = st.text_input(
            "📌 Subject",
            value=st.session_state.es_subject,
            placeholder="URGENT: Your account has been suspended",
            key="es_subject_input",
        )

        with st.expander("⚙️ Technical headers (optional)"):
            headers_val = st.text_area(
                "Raw headers",
                value=st.session_state.es_headers,
                height=100,
                placeholder="From: ...\nReply-To: ...\nX-Originating-IP: ...",
                key="es_headers_input",
                help="Copy from 'Show original' in your email client",
            )

        with st.expander("🔴 What to look for"):
            for flag, example in _RED_FLAGS:
                st.markdown(f"**{flag}** — *{example}*")

    with col_body_col:
        st.markdown("#### Email body")
        body = st.text_area(
            "Email body",
            value=st.session_state.es_body,
            height=340,
            placeholder="Paste the full email text here...",
            key="es_body_input",
            label_visibility="collapsed",
        )

    st.markdown("---")
    col_pad_l, col_load_btn, col_gap, col_analyze_btn, col_pad_r = st.columns([1, 1.4, 0.2, 1.4, 1])
    with col_load_btn:
        load_email_bottom = st.button(
            "⬆ Load Example",
            key="load_email_bottom",
            use_container_width=True,
        )
    with col_analyze_btn:
        analyze = st.button(
            "🔍 Check Email",
            type="primary",
            use_container_width=True,
            key="analyze_email_btn",
        )

    # Handle bottom Load click
    if load_email_bottom:
        if example_key != "— choose example —":
            ex = _EXAMPLES[example_key]
            st.session_state.es_sender = ex["sender"]
            st.session_state.es_subject = ex["subject"]
            st.session_state.es_body = ex["body"]
            st.session_state.es_headers = ex["headers"]
            st.rerun()
        else:
            st.info("👆 Select an example from the dropdown above first.")

    if analyze:
        full_text = _build_email_text(sender, subject, body, headers_val)
        if len(full_text.strip()) < 20:
            st.warning("⚠️ Enter at least a sender address and subject line.")
        else:
            with st.spinner("Analyzing email..."):
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
                        "📧 **Action required:** Do NOT click any links. "
                        "Contact the organization directly via their official website. Mark as spam."
                    )
                elif verdict == "Suspicious":
                    st.warning(
                        "📧 **Caution:** Verify the sender domain manually. "
                        "Do not reply or click any links until confirmed safe."
                    )
