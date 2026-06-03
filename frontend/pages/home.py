"""
frontend/pages/home.py - EN Landing Page ScamSence

Dark-only theme. English audience.
Sections: Hero -> Social Proof -> Examples -> How It Works -> Pricing -> Footer
"""
import streamlit as st

# ── Fixed dark CSS ───────────────────────────────────────────────────────────
_CSS_BASE = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');"
    "* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }"
    ".block-container { padding-top: 0 !important; max-width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; }"
    ".stApp { background-color: #09090f !important; }"
    "h1,h2,h3,h4,p,span,label,div { color: #f1f3f9 !important; }"
    "hr { border-color: #1c2040 !important; }"
    ".stButton > button { font-family: 'Inter', sans-serif !important; }"
    ".stButton > button[kind='primary'] { background: linear-gradient(135deg,#5865f2,#4752c4) !important; border: none !important; font-weight: 700 !important; font-size: 1rem !important; border-radius: 10px !important; padding: 0.6rem 1.5rem !important; box-shadow: 0 4px 20px rgba(88,101,242,0.35) !important; color: #fff !important; }"
    ".stButton > button[kind='primary']:hover { background: linear-gradient(135deg,#6875f5,#5865f2) !important; transform: translateY(-1px); }"
    ".stButton > button:not([kind='primary']) { background: rgba(255,255,255,0.05) !important; border: 1px solid #2d3154 !important; color: #c5cae9 !important; border-radius: 10px !important; }"
    "[data-testid='stSidebar'] { background-color: #0d0f1e !important; border-right: 1px solid #1c2040 !important; }"
    "[data-testid='stSidebar'] * { color: #c5cae9 !important; }"
    ".stTextArea textarea, .stTextInput input, .stSelectbox div { background-color: #131627 !important; color: #f1f3f9 !important; border-color: #2d3154 !important; }"
    ".stMetric { background: #131627; border: 1px solid #1c2040; border-radius: 10px; padding: 12px; }"
    ".stMetric label { color: #8892aa !important; font-size: 0.8rem !important; }"
    ".stMetric [data-testid='stMetricValue'] { color: #f1f3f9 !important; font-size: 1.2rem !important; font-weight: 700 !important; }"
    ".stExpander { background: #131627 !important; border: 1px solid #1c2040 !important; border-radius: 10px !important; }"
    ".stAlert { background: #131627 !important; border-radius: 10px !important; }"
    "#MainMenu { visibility: hidden; } footer { visibility: hidden; }"
    "</style>"
)

_CSS_LANDING = (
    "<style>"
    ".hero { background: linear-gradient(160deg,#09090f 0%,#0e1128 45%,#09090f 100%); padding: 80px 24px 60px; text-align: center; border-bottom: 1px solid #1c2040; position: relative; overflow: hidden; }"
    ".hero::before { content:''; position:absolute; top:-120px; left:50%; transform:translateX(-50%); width:800px; height:800px; background:radial-gradient(circle,rgba(88,101,242,0.1) 0%,transparent 65%); pointer-events:none; }"
    ".hero::after { content:''; position:absolute; bottom:-100px; right:-100px; width:400px; height:400px; background:radial-gradient(circle,rgba(255,59,59,0.06) 0%,transparent 65%); pointer-events:none; }"
    ".h-badge { display:inline-flex; align-items:center; gap:6px; background:rgba(88,101,242,0.1); border:1px solid rgba(88,101,242,0.3); color:#a5b4fc; font-size:0.72rem; font-weight:700; padding:5px 14px; border-radius:100px; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:24px; }"
    ".h-title { font-size:clamp(2.2rem,5vw,3.6rem); font-weight:900; line-height:1.1; color:#fff !important; margin:0 0 20px; letter-spacing:-0.03em; }"
    ".h-red { background:linear-gradient(135deg,#ff3b3b,#ff7070); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }"
    ".h-sub { font-size:1.1rem; color:#8892aa !important; max-width:560px; margin:0 auto 40px; line-height:1.8; }"
    ".h-trust { display:flex; justify-content:center; gap:32px; flex-wrap:wrap; margin-top:48px; padding-top:28px; border-top:1px solid #1c2040; }"
    ".trust-item { text-align:center; }"
    ".trust-n { font-size:1.6rem; font-weight:800; color:#5865f2 !important; }"
    ".trust-l { font-size:0.72rem; color:#5a6380 !important; margin-top:2px; letter-spacing:0.04em; text-transform:uppercase; }"
    ".sec { max-width:1100px; margin:0 auto; padding:64px 24px; }"
    ".sec-tag { font-size:0.7rem; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#5865f2 !important; margin-bottom:10px; }"
    ".sec-h { font-size:2rem; font-weight:800; color:#fff !important; margin:0 0 10px; letter-spacing:-0.02em; }"
    ".sec-s { color:#8892aa !important; font-size:0.95rem; margin-bottom:40px; max-width:520px; }"
    ".divider { border:none; border-top:1px solid #1c2040; margin:0; }"
    ".cases { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }"
    ".cc { background:#0f1220; border:1px solid #1c2040; border-radius:14px; padding:22px; position:relative; overflow:hidden; transition:border-color 0.2s; }"
    ".cc:hover { border-color:#2d3154; }"
    ".cc::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }"
    ".cc.r::before { background:linear-gradient(90deg,#ff3b3b,#ff6b6b); }"
    ".cc.a::before { background:linear-gradient(90deg,#f59e0b,#fbbf24); }"
    ".cc.g::before { background:linear-gradient(90deg,#10b981,#34d399); }"
    ".vb { display:inline-flex; align-items:center; gap:4px; font-size:0.68rem; font-weight:700; padding:3px 9px; border-radius:6px; margin-bottom:10px; letter-spacing:0.05em; text-transform:uppercase; }"
    ".vb.r { background:rgba(255,59,59,0.12); color:#ff6b6b !important; }"
    ".vb.a { background:rgba(245,158,11,0.12); color:#fbbf24 !important; }"
    ".vb.g { background:rgba(16,185,129,0.12); color:#34d399 !important; }"
    ".ct { font-size:0.67rem; color:#5a6380 !important; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; }"
    ".cx { font-size:0.84rem; color:#b8bdd0 !important; line-height:1.65; font-style:italic; margin-bottom:14px; border-left:2px solid #1c2040; padding-left:10px; }"
    ".cp { font-size:1.9rem; font-weight:900; }"
    ".cp.r { color:#ff3b3b !important; } .cp.a { color:#f59e0b !important; } .cp.g { color:#10b981 !important; }"
    ".cpl { font-size:0.7rem; color:#5a6380 !important; margin-bottom:12px; }"
    ".cfl { display:flex; flex-wrap:wrap; gap:5px; }"
    ".cf { background:rgba(255,255,255,0.03); border:1px solid #1c2040; color:#6b7280 !important; font-size:0.64rem; padding:2px 7px; border-radius:4px; }"
    ".steps { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }"
    ".sc { background:#0f1220; border:1px solid #1c2040; border-radius:14px; padding:24px; }"
    ".sn { width:36px; height:36px; border-radius:9px; background:linear-gradient(135deg,#5865f2,#4752c4); display:flex; align-items:center; justify-content:center; font-size:0.95rem; font-weight:800; color:#fff !important; margin-bottom:14px; }"
    ".st { font-size:0.92rem; font-weight:700; color:#fff !important; margin-bottom:7px; }"
    ".sd { font-size:0.82rem; color:#8892aa !important; line-height:1.65; }"
    ".plans { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }"
    ".pc { background:#0f1220; border:1px solid #1c2040; border-radius:16px; padding:28px; position:relative; }"
    ".pc.pop { background:linear-gradient(145deg,#131838,#161d42); border-color:#5865f2; }"
    ".pop-tag { position:absolute; top:-13px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#5865f2,#4752c4); color:#fff !important; font-size:0.67rem; font-weight:700; padding:4px 14px; border-radius:100px; letter-spacing:0.06em; white-space:nowrap; }"
    ".pt { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#5a6380 !important; margin-bottom:6px; }"
    ".pt.pro { color:#a5b4fc !important; } .pt.prem { color:#f59e0b !important; }"
    ".pp { font-size:2rem; font-weight:900; color:#fff !important; }"
    ".pp sub { font-size:0.85rem; font-weight:400; color:#5a6380 !important; }"
    ".pp .slash { font-size:0.9rem; color:#5a6380 !important; }"
    ".pyear { font-size:0.75rem; color:#34d399 !important; margin:2px 0 4px; }"
    ".pdesc { font-size:0.8rem; color:#8892aa !important; margin-bottom:18px; padding-bottom:16px; border-bottom:1px solid #1c2040; }"
    ".pfl { list-style:none; padding:0; margin:0; }"
    ".pfl li { font-size:0.83rem; color:#c5cae9 !important; padding:5px 0; display:flex; align-items:flex-start; gap:7px; }"
    ".ck { color:#5865f2 !important; font-weight:700; flex-shrink:0; }"
    ".cx2 { color:#2d3154 !important; flex-shrink:0; }"
    ".dim { color:#3a4060 !important; }"
    ".pro-f { color:#a5b4fc !important; font-weight:600; }"
    ".prem-f { color:#fbbf24 !important; font-weight:600; }"
    ".footer-w { background:#06070e; border-top:1px solid #1c2040; padding:32px 24px; text-align:center; }"
    ".f-logo { font-size:1.1rem; font-weight:800; color:#fff !important; margin-bottom:6px; }"
    ".f-tag { color:#5a6380 !important; font-size:0.8rem; margin-bottom:14px; }"
    ".f-links { display:flex; justify-content:center; gap:24px; flex-wrap:wrap; margin-bottom:14px; }"
    ".f-links a { color:#5a6380 !important; font-size:0.78rem; text-decoration:none; }"
    ".f-copy { color:#2d3154 !important; font-size:0.72rem; }"
    "</style>"
)

_HERO = (
    '<div class="hero">'
    '<div class="h-badge">&#128737; AI-Powered Scam Detection &middot; 2026</div>'
    '<h1 class="h-title">AI That <span class="h-red">Detects Scams</span><br>Before They Get You</h1>'
    '<p class="h-sub">Paste any email, message, link or phone script &mdash; '
    'get a verdict in seconds. 30+ detection patterns, real scam database.</p>'
    '<div class="h-trust">'
    '<div class="trust-item"><div class="trust-n">30+</div><div class="trust-l">Detection patterns</div></div>'
    '<div class="trust-item"><div class="trust-n">5</div><div class="trust-l">Check types</div></div>'
    '<div class="trust-item"><div class="trust-n">&lt;2s</div><div class="trust-l">Analysis time</div></div>'
    '<div class="trust-item"><div class="trust-n">Free</div><div class="trust-l">Start now</div></div>'
    '</div></div>'
)

_CASES = (
    '<div class="sec">'
    '<div class="sec-tag">&#128308; Real Scam Cases</div>'
    '<div class="sec-h">We see through scammers instantly</div>'
    '<p class="sec-s">Real scam messages we caught. Try submitting them yourself &mdash; get the same result.</p>'
    '<div class="cases">'

    '<div class="cc r">'
    '<span class="vb r">&#9940; SCAM</span>'
    '<div class="ct">Bank Phishing</div>'
    '<div class="cx">&ldquo;Your Chase Bank account has been suspended due to suspicious activity. '
    'Verify your identity immediately: http://chase-secure-verify.xyz/login&rdquo;</div>'
    '<div class="cp r">96%</div>'
    '<div class="cpl">scam probability</div>'
    '<div class="cfl">'
    '<span class="cf">&#127970; Bank impersonation</span>'
    '<span class="cf">&#9200; Urgency pressure</span>'
    '<span class="cf">&#128279; Phishing domain</span>'
    '</div></div>'

    '<div class="cc r">'
    '<span class="vb r">&#9940; SCAM</span>'
    '<div class="ct">Lottery / Prize</div>'
    '<div class="cx">&ldquo;Congratulations! You&rsquo;ve won an Apple iPhone 15 Pro. '
    'To claim your prize pay a $4.99 shipping fee. Offer expires in 24 hours.&rdquo;</div>'
    '<div class="cp r">97%</div>'
    '<div class="cpl">scam probability</div>'
    '<div class="cfl">'
    '<span class="cf">&#127873; Too good to be true</span>'
    '<span class="cf">&#128179; Fee required</span>'
    '<span class="cf">&#9200; Fake deadline</span>'
    '</div></div>'

    '<div class="cc a">'
    '<span class="vb a">&#9888; LIKELY SCAM</span>'
    '<div class="ct">Investment / Crypto</div>'
    '<div class="cx">&ldquo;Hey! I&rsquo;ve been trading crypto for 3 years, my portfolio is up +847% this year. '
    'I can add you to my private group &mdash; first month free.&rdquo;</div>'
    '<div class="cp a">89%</div>'
    '<div class="cpl">scam probability</div>'
    '<div class="cfl">'
    '<span class="cf">&#128176; Unrealistic returns</span>'
    '<span class="cf">&#128055; Pig butchering</span>'
    '<span class="cf">&#128202; Crypto scheme</span>'
    '</div></div>'

    '</div></div>'
)

_HOW = (
    '<div class="sec">'
    '<div class="sec-tag">&#9881; How It Works</div>'
    '<div class="sec-h">Three steps to stay safe</div>'
    '<p class="sec-s">No registration. No tracking. Just paste the text and get your answer.</p>'
    '<div class="steps">'

    '<div class="sc"><div class="sn">1</div>'
    '<div class="st">Paste suspicious content</div>'
    '<p class="sd">Email, SMS, ad, link, or phone script &mdash; any format. '
    'Select content type for more accurate analysis.</p></div>'

    '<div class="sc"><div class="sn">2</div>'
    '<div class="st">AI analyzes in &lt;2 seconds</div>'
    '<p class="sd">30+ pattern checks: urgency, impersonation, '
    'too-good-to-be-true, suspicious URLs, crypto schemes.</p></div>'

    '<div class="sc"><div class="sn">3</div>'
    '<div class="st">Get verdict + explanation</div>'
    '<p class="sd">Clear verdict (Scam / Suspicious / Legitimate), '
    'red flags with severity, and specific action recommendations.</p></div>'

    '<div class="sc"><div class="sn">4</div>'
    '<div class="st">Stay protected</div>'
    '<p class="sd">Save your check history, get PDF reports, '
    'and protect your team with Pro and Premium plans.</p></div>'

    '</div></div>'
)

_PRICING = (
    '<div class="sec" style="text-align:center;">'
    '<div class="sec-tag">&#128179; Pricing</div>'
    '<div class="sec-h">Start for free</div>'
    '<p class="sec-s" style="margin:0 auto 40px;">Free plan covers personal use. '
    'Upgrade for unlimited checks, history, and advanced features.</p>'
    '<div class="plans">'

    '<div class="pc">'
    '<div class="pt">Free</div>'
    '<div class="pp">$0<span class="slash"> / mo</span></div>'
    '<div class="pyear">&nbsp;</div>'
    '<div class="pdesc">Everything you need to start</div>'
    '<ul class="pfl">'
    '<li><span class="ck">&#10003;</span> 5 checks per day per IP</li>'
    '<li><span class="ck">&#10003;</span> Text &amp; SMS analysis</li>'
    '<li><span class="ck">&#10003;</span> Email check</li>'
    '<li><span class="ck">&#10003;</span> URL analysis</li>'
    '<li><span class="ck">&#10003;</span> Basic red flags</li>'
    '<li><span class="cx2">&#10007;</span> <span class="dim">Check history</span></li>'
    '<li><span class="cx2">&#10007;</span> <span class="dim">PDF reports</span></li>'
    '<li><span class="cx2">&#10007;</span> <span class="dim">Voice analysis</span></li>'
    '</ul></div>'

    '<div class="pc pop">'
    '<div class="pop-tag">&#11088; MOST POPULAR</div>'
    '<div class="pt pro">Pro</div>'
    '<div class="pp">$9<span class="slash"> / mo</span></div>'
    '<div class="pyear">or $7/mo billed annually &mdash; save 22%</div>'
    '<div class="pdesc">For serious protection</div>'
    '<ul class="pfl">'
    '<li><span class="ck">&#10003;</span> Unlimited checks</li>'
    '<li><span class="ck">&#10003;</span> Text, SMS, Email, URL</li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-f">Full check history</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-f">PDF reports</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-f">Priority analysis</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-f">Browser extension</span> <em style="color:#5a6380;font-size:0.75rem;">(coming)</em></li>'
    '<li><span class="cx2">&#10007;</span> <span class="dim">Voice analysis</span></li>'
    '<li><span class="cx2">&#10007;</span> <span class="dim">Team access</span></li>'
    '</ul></div>'

    '<div class="pc">'
    '<div class="pt prem">Premium</div>'
    '<div class="pp">$19<span class="slash"> / mo</span></div>'
    '<div class="pyear">or $15/mo billed annually &mdash; save 21%</div>'
    '<div class="pdesc">For teams &amp; power users</div>'
    '<ul class="pfl">'
    '<li><span class="ck">&#10003;</span> Everything in Pro</li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">Voice analysis (Whisper)</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">Team access (5 seats)</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">API access</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">YouTube transcript scan</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">Bulk analysis</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">Priority support</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="prem-f">Custom integrations</span></li>'
    '</ul></div>'

    '</div></div>'
)

_FOOTER = (
    '<div class="footer-w">'
    '<div class="f-logo">&#128737; ScamSence</div>'
    '<div class="f-tag">AI-powered Scam &amp; Fraud Detection</div>'
    '<div class="f-links">'
    '<a href="#">About</a><a href="#">API</a><a href="#">Privacy</a>'
    '<a href="#">Terms</a><a href="#">Contact</a>'
    '</div>'
    '<div class="f-copy">&copy; 2026 ScamSence &middot; Built to protect people from scammers</div>'
    '</div>'
)


def render() -> None:
    """Renders the ScamSence EN landing page (dark-only)."""
    st.markdown(_CSS_BASE + _CSS_LANDING, unsafe_allow_html=True)

    # Hero
    st.markdown(_HERO, unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1.8, 1.8, 1.8])
    with col_c:
        if st.button("Analyze Now — It's Free", type="primary",
                     use_container_width=True, key="hero_cta"):
            st.session_state["page_nav"] = "Analyzer"
            st.rerun()

    # Real examples
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_CASES, unsafe_allow_html=True)
    col_l2, col_c2, col_r2 = st.columns([2, 1.5, 2])
    with col_c2:
        if st.button("Try it yourself →", use_container_width=True, key="cases_cta"):
            st.session_state["page_nav"] = "Analyzer"
            st.rerun()

    # How it works
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_HOW, unsafe_allow_html=True)

    # Pricing
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_PRICING, unsafe_allow_html=True)
    col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([1, 1, 0.5, 1, 1])
    with col_p2:
        if st.button("Start Free", use_container_width=True, key="free_cta"):
            st.session_state["page_nav"] = "Analyzer"
            st.rerun()
    with col_p4:
        if st.button("Get Pro →", type="primary", use_container_width=True, key="pro_cta"):
            st.session_state["page_nav"] = "Analyzer"
            st.rerun()

    # Footer
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_FOOTER, unsafe_allow_html=True)
