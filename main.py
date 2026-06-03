"""
main.py - ScamSence MVP entry point (Streamlit)

Dark-only theme. No light/dark toggle.
Navigation: Home | Analyzer | Email Check | URL Check

Run:
  uvicorn backend.app:app --reload   (terminal 1)
  streamlit run main.py              (terminal 2)
"""
import streamlit as st

st.set_page_config(
    page_title="ScamSence — AI Scam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Imports after set_page_config
from frontend.pages.home import render as render_home
from frontend.pages.analyzer import render as render_analyzer
from frontend.pages.email_check import render as render_email
from frontend.pages.url_check import render as render_url
from frontend.pages.text_check import render as render_text

# ── Fixed dark theme CSS (applied globally) ───────────────────────────────────
_DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #09090f !important; }
.block-container { background-color: #09090f !important; padding-top: 1.5rem; }
h1,h2,h3,h4,p,span,label { color: #f1f3f9 !important; }
hr { border-color: #1c2040 !important; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #0d0f1e !important; border-right: 1px solid #1c2040 !important; }
[data-testid="stSidebar"] * { color: #c5cae9 !important; }
[data-testid="stSidebar"] .stRadio label { color: #c5cae9 !important; }

/* Inputs */
.stTextArea textarea, .stTextInput input { background-color: #131627 !important; color: #f1f3f9 !important; border-color: #2d3154 !important; }
.stSelectbox > div { background-color: #131627 !important; color: #f1f3f9 !important; }
div[data-baseweb="select"] { background-color: #131627 !important; }

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5865f2, #4752c4) !important;
    border: none !important; font-weight: 700 !important;
    border-radius: 10px !important; color: #fff !important;
    box-shadow: 0 4px 16px rgba(88,101,242,0.3) !important;
}
.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg,#6875f5,#5865f2) !important; }
.stButton > button:not([kind="primary"]) {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid #2d3154 !important;
    color: #c5cae9 !important; border-radius: 10px !important;
}

/* Expanders, alerts */
[data-testid="stExpander"] { background: #0f1220 !important; border: 1px solid #1c2040 !important; border-radius: 10px !important; }
.stAlert { background: #0f1220 !important; border-radius: 10px !important; }

/* Progress bar */
.stProgress > div > div { background: #5865f2 !important; }

/* Metrics */
[data-testid="stMetric"] { background: #0f1220; border: 1px solid #1c2040; border-radius: 10px; padding: 12px; }
[data-testid="stMetricValue"] { color: #f1f3f9 !important; }
[data-testid="stMetricLabel"] { color: #8892aa !important; }
</style>
"""


def _render_sidebar() -> str:
    """Renders sidebar navigation. Returns selected page name."""
    with st.sidebar:
        # Logo
        st.markdown(
            '<div style="padding:8px 0 16px;">'
            '<span style="font-size:1.2rem;font-weight:900;color:#fff;">&#128737; ScamSence</span><br>'
            '<span style="font-size:0.75rem;color:#5a6380;">AI Scam & Fraud Detector</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Navigation — handle page_nav from CTA buttons on landing page
        nav_options = ["🏠 Home", "🔍 Analyzer", "📧 Email Check", "🔗 URL Check"]

        # Map page_nav shortcuts from landing page buttons
        nav_map = {"Analyzer": "🔍 Analyzer"}
        if "page_nav" in st.session_state:
            target = nav_map.get(st.session_state.pop("page_nav"), None)
            if target and target in nav_options:
                default_idx = nav_options.index(target)
            else:
                default_idx = 0
        else:
            default_idx = 0

        page = st.radio(
            "Navigation",
            options=nav_options,
            index=default_idx,
            label_visibility="collapsed",
            key="main_nav",
        )

        st.markdown("---")

        # Recent checks history
        history = st.session_state.get("history", [])
        if history:
            st.markdown('<span style="font-size:0.75rem;font-weight:700;color:#5a6380;text-transform:uppercase;letter-spacing:0.08em;">Recent Checks</span>', unsafe_allow_html=True)
            for item in history[:5]:
                verdict = item.get("verdict", "?")
                prob = item.get("probability", 0)
                emoji = {"Scam": "🚨", "Likely Scam": "⚠️", "Suspicious": "🔍", "Legitimate": "✅"}.get(verdict, "❓")
                st.markdown(
                    f'<div style="padding:6px 0;border-bottom:1px solid #1c2040;">'
                    f'{emoji} <span style="color:#c5cae9;font-size:0.8rem;">{item["text"][:35]}…</span><br>'
                    f'<span style="color:#5a6380;font-size:0.72rem;">{verdict} · {prob}%</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("")

        st.markdown("---")

        # Status footer
        st.markdown(
            '<span style="font-size:0.72rem;color:#3a4060;">ScamSence MVP v0.1</span><br>'
            '<span style="font-size:0.72rem;color:#3a4060;">Days 1–6 ✅</span>',
            unsafe_allow_html=True,
        )

    return page


def main() -> None:
    # Inject global dark CSS
    st.markdown(_DARK_CSS, unsafe_allow_html=True)

    page = _render_sidebar()

    if page == "🏠 Home":
        render_home()
    elif page == "🔍 Analyzer":
        render_analyzer()
    elif page == "📧 Email Check":
        render_email()
    elif page == "🔗 URL Check":
        render_url()


main()
