"""
main.py — Точка входа ScamSence MVP (Streamlit)

Запуск: streamlit run main.py
Требует: uvicorn backend.app:app --reload  (в отдельном терминале)
"""
import streamlit as st

st.set_page_config(
    page_title="ScamSence — Scam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.pages.text_check import render as render_text_check
from frontend.pages.home import render as render_home
from frontend.pages.email_check import render as render_email_check
from frontend.pages.url_check import render as render_url_check


def apply_theme() -> None:
    """Применяет светлую или тёмную тему через CSS-инъекцию."""
    dark = st.session_state.get("dark_mode", False)

    if dark:
        bg = "#0E1117"
        surface = "#1A1D27"
        text = "#FAFAFA"
        subtext = "#A0A0A0"
        border = "#2D2F3A"
        sidebar_bg = "#161820"
        btn_bg = "#FF4B4B"
        input_bg = "#1E2130"
    else:
        bg = "#FFFFFF"
        surface = "#F8F9FA"
        text = "#1A1A1A"
        subtext = "#666666"
        border = "#E0E0E0"
        sidebar_bg = "#F0F2F6"
        btn_bg = "#FF4B4B"
        input_bg = "#FFFFFF"

    st.markdown(f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* App background */
        .stApp {{
            background-color: {bg};
            color: {text};
        }}

        /* Main content area */
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            background-color: {bg};
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
        }}
        [data-testid="stSidebar"] * {{
            color: {text} !important;
        }}
        div[data-testid="stSidebarContent"] {{
            padding-top: 1rem;
        }}

        /* Text and headings */
        h1, h2, h3, h4, p, span, label {{
            color: {text} !important;
        }}

        /* Subtext / captions */
        .stCaption, small, .st-emotion-cache-16idsys {{
            color: {subtext} !important;
        }}

        /* Inputs */
        .stTextArea textarea, .stTextInput input, .stSelectbox div {{
            background-color: {input_bg} !important;
            color: {text} !important;
            border-color: {border} !important;
        }}

        /* Cards / containers */
        [data-testid="stExpander"] {{
            background-color: {surface};
            border-color: {border};
        }}

        /* Primary button */
        .stButton > button[kind="primary"] {{
            background: {btn_bg};
            border: none;
            font-weight: 600;
            font-size: 1rem;
            color: white !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #E03030;
        }}

        /* Info/success/warning boxes */
        .stAlert {{
            background-color: {surface};
        }}

        /* Markdown blockquote */
        blockquote {{
            border-left: 3px solid {btn_bg};
            background-color: {surface};
            color: {text} !important;
            padding: 8px 16px;
            border-radius: 4px;
        }}

        /* Divider */
        hr {{
            border-color: {border};
        }}

        /* Progress bar */
        .stProgress > div > div {{
            background-color: {btn_bg};
        }}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## 🛡️ ScamSence")
        st.markdown("*AI-powered fraud detector*")

        # ── Dark mode toggle ─────────────────────────────────────────────
        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False

        dark = st.session_state.dark_mode
        toggle_label = "🌙 Dark mode" if not dark else "☀️ Light mode"

        if st.button(toggle_label, key="theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("---")

        page = st.radio(
            "Navigation",
            options=["🏠 Home", "💬 Text Check", "📧 Email Check", "🔗 URL Check"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        if "history" in st.session_state and st.session_state.history:
            st.markdown("### 📋 Recent Checks")
            for item in st.session_state.history[:5]:
                verdict = item["verdict"]
                emoji = {"Scam": "🚨", "Likely Scam": "⚠️", "Suspicious": "🔍", "Legitimate": "✅"}.get(verdict, "❓")
                st.markdown(
                    f"{emoji} **{item['probability']}%** — {item['text'][:40]}...",
                    help=f"Type: {item.get('content_type','text')} | Verdict: {verdict}",
                )

        st.markdown("---")
        st.caption("ScamSence MVP v0.1 · Days 1–6 ✅")
        st.caption("API: http://127.0.0.1:8000/docs")

    return page


def main() -> None:
    apply_theme()
    page = render_sidebar()

    if page == "🏠 Home":
        render_home()
    elif page == "💬 Text Check":
        render_text_check()
    elif page == "📧 Email Check":
        render_email_check()
    elif page == "🔗 URL Check":
        render_url_check()


main()
