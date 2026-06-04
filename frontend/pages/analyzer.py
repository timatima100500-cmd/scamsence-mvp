"""
frontend/pages/analyzer.py - Unified Analyzer Page

Supports: text, email, URL, SMS content types.
File upload: audio files shown as Pro feature (coming Day 9).
Verdict output: strict format matching CLAUDE.md spec.
"""
import streamlit as st
import requests
import json

from frontend.components.result_card import render_result_card

API_URL = "http://127.0.0.1:8000/api/v1/analyze"

CONTENT_TYPES = {
    "Auto-detect": "text",
    "📧 Email": "email",
    "💬 SMS / Message": "sms",
    "🔗 URL / Link": "url",
    "📋 Ad / Listing": "text",
    "📞 Phone Script": "text",
}

PLACEHOLDERS = {
    "Auto-detect": "Paste any suspicious message, email, link, or phone script here...",
    "📧 Email": "From: security@bank-alert.xyz\nSubject: URGENT: Your account suspended\n\nDear customer, your account has been...",
    "💬 SMS / Message": "Your package could not be delivered. Update your address: http://usps-track.xyz/update",
    "🔗 URL / Link": "https://paypa1.com/login/security-verify",
    "📋 Ad / Listing": "Earn $500/day working from home! No experience needed. Click here to apply...",
    "📞 Phone Script": "Hi, this is Officer Johnson from the IRS. You owe $3,200 in back taxes...",
}

EXAMPLES = {
    "🏦 Bank phishing email": (
        "📧 Email",
        "From: security@chase-bank-alert.xyz\nSubject: URGENT: Account Suspended\n\n"
        "Dear Chase Customer,\n\nYour account has been temporarily suspended due to suspicious activity.\n"
        "To restore access, verify your information immediately:\n"
        "http://chase-secure-verify.xyz/login\n\n"
        "Failure to verify within 24 hours will result in permanent account closure.\n\nChase Security Team"
    ),
    "🎰 iPhone lottery scam": (
        "💬 SMS / Message",
        "Congratulations! You've been selected to receive a FREE Apple iPhone 15 Pro. "
        "This is a limited time offer - claim your prize now by paying only $4.99 shipping: "
        "http://bit.ly/apple-prize-claim2026. Offer expires in 24 hours!"
    ),
    "🐷 Pig butchering crypto": (
        "💬 SMS / Message",
        "Hey! Sorry to bother you, I think I messaged the wrong person but we got talking and "
        "I realized you seem really smart. I've been making great returns on crypto lately - "
        "up 847% this year. Would you like me to show you my strategy? No pressure at all."
    ),
    "🔗 Typosquatting URL": (
        "🔗 URL / Link",
        "https://paypa1.com/login/security-check?redirect=account-verify"
    ),
    "👨‍💻 Tech support scam": (
        "📞 Phone Script",
        "Hello, this is Microsoft Support. We've detected a serious virus on your computer that "
        "is stealing your personal information. Your Windows license has been compromised. "
        "You must call us immediately at 1-800-555-0199 or your computer will be permanently disabled."
    ),
    "🏛️ IRS government scam": (
        "📞 Phone Script",
        "This is a final warning from the IRS Criminal Investigation Division. "
        "You owe $3,847 in unpaid taxes. A federal warrant has been issued for your arrest. "
        "To avoid arrest, call 1-888-555-0142 immediately and pay via gift cards."
    ),
}


def _call_api(content: str, content_type: str) -> dict | None:
    """Sends content to analysis API. Returns result dict or None on error."""
    try:
        resp = requests.post(
            API_URL,
            json={"content": content, "content_type": content_type},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start it: `uvicorn backend.app:app --reload`")
    except requests.exceptions.Timeout:
        st.error("⏱️ API did not respond in 30 seconds.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP error: {e}")
    except json.JSONDecodeError:
        st.error("❌ Invalid response from API.")
    return None


def _verdict_color(verdict: str) -> str:
    return {
        "Scam": "#ff3b3b",
        "Likely Scam": "#f59e0b",
        "Suspicious": "#f59e0b",
        "Legitimate": "#10b981",
    }.get(verdict, "#8892aa")


def render() -> None:
    """Renders the unified Analyzer page."""

    # Page header
    st.markdown(
        "<h2 style='color:#fff;margin-bottom:4px;'>&#128269; ScamSence Analyzer</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8892aa;margin-bottom:0;'>Paste any suspicious content — get an AI verdict in seconds.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Top row: content type + example loader ────────────────────────────────
    col_type, col_ex, col_load = st.columns([1.5, 2.5, 0.8])

    with col_type:
        content_type_label = st.selectbox(
            "Content type",
            options=list(CONTENT_TYPES.keys()),
            key="az_content_type",
        )

    with col_ex:
        example_key = st.selectbox(
            "Load an example",
            options=["— choose example —"] + list(EXAMPLES.keys()),
            key="az_example_select",
        )

    with col_load:
        st.markdown("<br>", unsafe_allow_html=True)
        load_clicked = st.button("Load", key="az_load_btn", use_container_width=True)

    # Init session state
    if "az_text" not in st.session_state:
        st.session_state.az_text = ""
    if "az_type" not in st.session_state:
        st.session_state.az_type = "Auto-detect"

    if load_clicked and example_key != "— choose example —":
        ex_type, ex_text = EXAMPLES[example_key]
        st.session_state.az_text = ex_text
        st.session_state.az_type = ex_type
        st.rerun()

    st.markdown("---")

    # ── Main input area ───────────────────────────────────────────────────────
    col_input, col_upload = st.columns([2.5, 1])

    with col_input:
        placeholder = PLACEHOLDERS.get(content_type_label, PLACEHOLDERS["Auto-detect"])
        text_input = st.text_area(
            "Content to analyze",
            value=st.session_state.az_text,
            height=280,
            placeholder=placeholder,
            key="az_text_area",
            label_visibility="collapsed",
        )

    with col_upload:
        st.markdown("#### Upload file")

        # Text file upload
        uploaded_file = st.file_uploader(
            "Text / Email file",
            type=["txt", "eml", "msg"],
            key="az_file_upload",
            help="Upload .txt, .eml, or .msg files",
        )
        if uploaded_file:
            text_input = uploaded_file.read().decode("utf-8", errors="replace")
            st.success(f"✅ Loaded: {uploaded_file.name}")

        # Audio upload (Pro feature — UI only until Day 9)
        st.markdown("---")
        st.markdown(
            '<div style="background:rgba(0,148,212,0.07);border:1px solid rgba(0,148,212,0.22);'
            'border-radius:10px;padding:14px;">'
            '<div style="font-size:0.75rem;font-weight:700;color:#00b8f0;text-transform:uppercase;'
            'letter-spacing:0.08em;margin-bottom:8px;">&#127908; Voice Analysis</div>'
            '<div style="font-size:0.8rem;color:#8892aa;margin-bottom:10px;">'
            'Upload audio: MP3, WAV, M4A<br>'
            '<em>AI detects voice cloning, fake urgency, unnatural patterns.</em>'
            '</div>'
            '<div style="display:inline-block;background:linear-gradient(135deg,#0094d4,#005f8a);'
            'color:#fff;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:100px;">'
            '&#11088; PRO / PREMIUM</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.file_uploader(
            "Audio file (Pro)",
            type=["mp3", "wav", "m4a", "ogg"],
            key="az_audio_upload",
            disabled=True,
            help="Voice analysis coming in Premium plan",
        )

    # ── Char count + analyze button ───────────────────────────────────────────
    char_count = len(text_input) if text_input else 0
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        color = "#10b981" if char_count > 20 else "#5a6380"
        st.markdown(
            f'<p style="color:{color};font-size:0.8rem;margin:4px 0;">'
            f'{char_count} characters {" ✓ ready to analyze" if char_count > 20 else " — paste content above"}'
            f'</p>',
            unsafe_allow_html=True,
        )
    with col_btn:
        analyze = st.button(
            "&#128269; Analyze",
            type="primary",
            use_container_width=True,
            key="az_analyze_btn",
        )

    # ── Analysis ──────────────────────────────────────────────────────────────
    if analyze:
        content = text_input.strip() if text_input else ""
        if len(content) < 10:
            st.warning("⚠️ Please paste at least a few words to analyze.")
        else:
            api_type = CONTENT_TYPES.get(content_type_label, "text")
            with st.spinner("Analyzing..."):
                result = _call_api(content, api_type)

            if result:
                # Save to history
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.insert(0, {
                    "text": content[:60],
                    "verdict": result.get("verdict", "Unknown"),
                    "probability": result.get("scam_probability", 0),
                    "content_type": api_type,
                })

                st.markdown("---")

                # Verdict banner
                verdict = result.get("verdict", "Unknown")
                prob = result.get("scam_probability", 0)
                vc = _verdict_color(verdict)

                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.03);border:1px solid {vc}40;'
                    f'border-left:4px solid {vc};border-radius:12px;padding:20px 24px;margin-bottom:20px;">'
                    f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">'
                    f'<div><div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;'
                    f'text-transform:uppercase;color:#5a6380;">VERDICT</div>'
                    f'<div style="font-size:1.8rem;font-weight:900;color:{vc};">{verdict}</div></div>'
                    f'<div style="width:1px;height:48px;background:#1c2040;"></div>'
                    f'<div><div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;'
                    f'text-transform:uppercase;color:#5a6380;">SCAM PROBABILITY</div>'
                    f'<div style="font-size:1.8rem;font-weight:900;color:{vc};">{prob}%</div></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                # Full result card
                render_result_card(result)

                # Type-specific advice
                if verdict in ("Scam", "Likely Scam"):
                    advice = {
                        "email": "Do NOT click any links. Contact the organization directly via their official website. Mark as spam.",
                        "url": "Do NOT visit this URL. Report phishing at https://safebrowsing.google.com/safebrowsing/report_phish/",
                        "sms": "Block the number. Do not reply or click links. Report to your carrier.",
                    }.get(api_type, "Do NOT engage with this content. Block and report the sender.")
                    st.error(f"&#128680; **Action required:** {advice}")
