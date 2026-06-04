"""
main.py - ScamSence MVP entry point

Premium dark design (Linear/Arc style).
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

from frontend.pages.home import render as render_home
from frontend.pages.analyzer import render as render_analyzer
from frontend.pages.email_check import render as render_email
from frontend.pages.url_check import render as render_url

# ── Global Design System CSS ─────────────────────────────────────────────────
# Killer-style: deep dark, cyan-blue accent, high contrast
_DS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

:root {
  --bg0: #07090e;
  --bg1: #0c0f18;
  --bg2: #111520;
  --bg3: #182030;
  --border: rgba(255,255,255,0.08);
  --border2: rgba(0,148,212,0.35);
  --text1: #e8f0ff;
  --text2: #7a8fa8;
  --text3: #3a4a5c;
  --accent: #0094d4;
  --accent2: #00b8f0;
  --red: #ef4444;
  --green: #22c55e;
  --amber: #f59e0b;
}

* { font-family: 'Inter', -apple-system, sans-serif !important; box-sizing: border-box; }

/* ── App shell ── */
.stApp { background: var(--bg0) !important; }
.block-container { background: var(--bg0) !important; padding-top: 1rem !important; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden !important; }
[data-testid="stToolbar"], .stDeployButton, [data-testid="stDecoration"] { display: none !important; }

/* ── Typography ── */
h1, h2, h3, h4 { color: var(--text1) !important; letter-spacing: -0.02em; }
p, span, label, div { color: var(--text1) !important; }
.stCaption, small { color: var(--text2) !important; }
hr { border-color: var(--border) !important; border-top-width: 1px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * { color: var(--text2) !important; }
[data-testid="stSidebarContent"] { padding-top: 1.5rem !important; }

/* ── Radio nav (sidebar) ── */
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
  color: var(--text2) !important;
  font-size: 0.88rem;
  padding: 0.3rem 0;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) [data-testid="stMarkdownContainer"] p {
  color: var(--text1) !important;
  font-weight: 600;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text1) !important;
  font-size: 0.9rem !important;
  transition: border-color 0.2s;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--border2) !important;
  box-shadow: 0 0 0 3px rgba(0,148,212,0.12) !important;
}

/* ── Selectbox — trigger (closed state) ── */
div[data-baseweb="select"] > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text1) !important;
}
div[data-baseweb="select"] > div:hover {
  border-color: var(--border2) !important;
}
/* selected value text */
div[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"] span,
div[data-baseweb="select"] > div > div > div,
div[data-baseweb="select"] > div span {
  color: var(--text1) !important;
}
/* dropdown arrow */
div[data-baseweb="select"] svg { fill: var(--text2) !important; }

/* ── Selectbox — dropdown popup ── */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
}
/* menu list */
ul[data-baseweb="menu"],
[data-baseweb="menu"] {
  background: var(--bg2) !important;
  padding: 4px !important;
}
/* individual options */
[role="option"] {
  background: var(--bg2) !important;
  border-radius: 6px !important;
  padding: 8px 12px !important;
  margin: 1px 0 !important;
}
[role="option"]:hover,
[role="option"][aria-selected="true"] {
  background: var(--bg3) !important;
}
/* option text — all children */
[role="option"] *,
[role="option"] span,
[role="option"] div,
[role="option"] p,
[data-baseweb="menu-item"],
[data-baseweb="menu-item"] * {
  color: var(--text1) !important;
  background: transparent !important;
}
/* highlighted/active option */
[role="option"][aria-selected="true"] * {
  color: var(--accent2) !important;
}
/* "no results" placeholder */
[data-baseweb="popover"] [role="listbox"] div {
  color: var(--text1) !important;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0094d4, #006fa8) !important;
  border: none !important;
  border-radius: 10px !important;
  color: #fff !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  padding: 0.55rem 1.4rem !important;
  box-shadow: 0 0 24px rgba(0,148,212,0.3), inset 0 1px 0 rgba(255,255,255,0.1) !important;
  transition: all 0.2s !important;
  letter-spacing: -0.01em !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #00b8f0, #0094d4) !important;
  box-shadow: 0 0 32px rgba(0,184,240,0.45) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text2) !important;
  font-size: 0.88rem !important;
  transition: all 0.2s !important;
}
.stButton > button:not([kind="primary"]):hover {
  border-color: var(--border2) !important;
  color: var(--text1) !important;
}

/* ── Expanders & Alerts ── */
[data-testid="stExpander"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text2) !important; }
.stAlert { background: var(--bg2) !important; border-radius: 12px !important; }
.stSuccess, .stInfo, .stWarning, .stError { background: var(--bg2) !important; }

/* ── Progress & Metrics ── */
.stProgress > div > div { background: var(--accent) !important; border-radius: 4px; }
[data-testid="stMetric"] {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem;
}
[data-testid="stMetricValue"] { color: var(--text1) !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: var(--text2) !important; font-size: 0.78rem !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--bg2) !important;
  border: 1px dashed rgba(0,148,212,0.25) !important;
  border-radius: 12px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Labels above inputs ── */
.stSelectbox label,
.stTextArea label,
.stTextInput label,
.stFileUploader label {
  color: var(--text2) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
}
</style>
"""


def _sidebar() -> str:
    """Renders sidebar. Returns active page label."""
    with st.sidebar:
        # Logo
        st.markdown(
            '<div style="padding:0 4px 20px;">'
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            '<div style="width:28px;height:28px;border-radius:8px;'
            'background:linear-gradient(135deg,#0094d4,#005f8a);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:14px;">&#128737;</div>'
            '<span style="font-size:1rem;font-weight:800;color:#e8f0ff;letter-spacing:-0.02em;">ScamSence</span>'
            '</div>'
            '<div style="font-size:0.72rem;color:#3a4a5c;letter-spacing:0.04em;padding-left:36px;">AI SCAM DETECTOR</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:0 -1rem 16px;"></div>', unsafe_allow_html=True)

        # Nav
        nav_options = ["🏠 Home", "🔍 Analyzer", "📧 Email Check", "🔗 URL Check"]

        # Handle CTA nav redirects from landing page
        default_idx = 0
        if "page_nav" in st.session_state:
            nav_map = {"Analyzer": "🔍 Analyzer"}
            target = nav_map.get(st.session_state.pop("page_nav"))
            if target in nav_options:
                default_idx = nav_options.index(target)

        page = st.radio(
            "nav",
            options=nav_options,
            index=default_idx,
            label_visibility="collapsed",
            key="main_nav",
        )

        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:0 -1rem 16px;"></div>', unsafe_allow_html=True)

        # Recent checks
        history = st.session_state.get("history", [])
        if history:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;'
                'text-transform:uppercase;color:#4a5872;margin-bottom:10px;">Recent</div>',
                unsafe_allow_html=True,
            )
            colors = {"Scam": "#ef4444", "Likely Scam": "#f59e0b", "Suspicious": "#f59e0b", "Legitimate": "#22c55e"}
            icons = {"Scam": "⛔", "Likely Scam": "⚠️", "Suspicious": "🔍", "Legitimate": "✅"}
            for item in history[:4]:
                v = item.get("verdict", "?")
                c = colors.get(v, "#8b9ab2")
                i = icons.get(v, "❓")
                st.markdown(
                    f'<div style="padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                    f'<div style="font-size:0.78rem;color:#8b9ab2;white-space:nowrap;overflow:hidden;'
                    f'text-overflow:ellipsis;max-width:180px;">{i} {item["text"][:32]}…</div>'
                    f'<div style="font-size:0.7rem;color:{c};margin-top:2px;">{v} · {item["probability"]}%</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Footer
        st.markdown(
            '<div style="position:absolute;bottom:20px;left:0;right:0;padding:0 1rem;">'
            '<div style="font-size:0.68rem;color:#2d3a52;">ScamSence MVP · Days 1–7 ✅</div>'
            '<div style="font-size:0.68rem;color:#2d3a52;margin-top:2px;">API: localhost:8000</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    return page


def main():
    st.markdown(_DS, unsafe_allow_html=True)
    page = _sidebar()

    if page == "🏠 Home":
        render_home()
    elif page == "🔍 Analyzer":
        render_analyzer()
    elif page == "📧 Email Check":
        render_email()
    elif page == "🔗 URL Check":
        render_url()


main()
