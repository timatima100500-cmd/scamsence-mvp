"""
frontend/pages/home.py - Premium Landing Page

Linear/Arc-style dark design. English audience.
All HTML is in one render() function using string constants.
"""
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# CSS — landing-specific (base DS is in main.py)
# ─────────────────────────────────────────────────────────────────────────────
_CSS = """<style>
/* ── Layout ── */
.lp { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
.lp-full { padding: 0; }
.divl { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 0; }

/* ── Hero ── */
.hero-wrap {
  position: relative; overflow: hidden;
  padding: 100px 24px 80px; text-align: center;
  background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0,148,212,0.12) 0%, transparent 70%);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.hero-glow-l {
  position: absolute; width: 500px; height: 500px; border-radius: 50%;
  background: radial-gradient(circle, rgba(0,148,212,0.10) 0%, transparent 70%);
  top: -200px; left: -150px; pointer-events: none;
}
.hero-glow-r {
  position: absolute; width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(circle, rgba(239,68,68,0.07) 0%, transparent 70%);
  bottom: -150px; right: -100px; pointer-events: none;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(0,148,212,0.08); border: 1px solid rgba(0,148,212,0.25);
  color: #00b8f0; font-size: 0.72rem; font-weight: 600;
  padding: 5px 14px; border-radius: 100px; letter-spacing: 0.06em;
  text-transform: uppercase; margin-bottom: 28px;
}
.badge-pulse {
  width: 6px; height: 6px; border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 0 rgba(34,197,94,0.4);
  animation: pulse 2s infinite;
  display: inline-block;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
  70% { box-shadow: 0 0 0 8px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}
.hero-h {
  font-size: clamp(2.6rem, 5.5vw, 4rem); font-weight: 900;
  line-height: 1.05; letter-spacing: -0.04em;
  color: #e8f0ff !important; margin: 0 0 20px;
  max-width: 820px; margin-left: auto; margin-right: auto;
}
.hero-grad {
  color: #00b8f0 !important;
}
.hero-sub {
  font-size: 1.1rem; line-height: 1.8; color: #7a8fa8 !important;
  max-width: 540px; margin: 0 auto 40px;
}
.hero-trust {
  display: flex; justify-content: center; gap: 48px; flex-wrap: wrap;
  padding-top: 32px; margin-top: 32px; border-top: 1px solid rgba(255,255,255,0.06);
}
.ht-item { text-align: center; }
.ht-n { font-size: 1.5rem; font-weight: 800; color: #e8f0ff !important; }
.ht-l { font-size: 0.7rem; color: #3a4a5c !important; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px; }

/* ── Social proof ── */
.sp-bar {
  display: flex; align-items: center; justify-content: center;
  gap: 12px; padding: 14px 24px; flex-wrap: wrap;
  background: rgba(0,148,212,0.04); border-bottom: 1px solid rgba(0,148,212,0.12);
}
.sp-avatars { display: flex; }
.sp-av {
  width: 26px; height: 26px; border-radius: 50%;
  border: 2px solid #07090e; margin-left: -8px;
  font-size: 0.6rem; font-weight: 700; color: #fff !important;
  display: flex; align-items: center; justify-content: center;
}
.sp-av:first-child { margin-left: 0; }
.sp-text { font-size: 0.82rem; color: #7a8fa8 !important; }
.sp-text b { color: #e8f0ff !important; }

/* ── Section ── */
.sec { padding: 80px 24px; max-width: 1100px; margin: 0 auto; }
.sec-tag { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0094d4 !important; margin-bottom: 12px; }
.sec-h { font-size: 2.1rem; font-weight: 800; color: #e8f0ff !important; letter-spacing: -0.03em; margin: 0 0 12px; }
.sec-s { font-size: 0.95rem; color: #7a8fa8 !important; line-height: 1.8; margin-bottom: 40px; max-width: 500px; }

/* ── Example cards ── */
.cards-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.card {
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px; padding: 22px; position: relative; overflow: hidden;
  transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
  cursor: default;
}
.card:hover { border-color: rgba(255,255,255,0.14); transform: translateY(-2px); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
.card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.card.red::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.card.amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.card.green::before { background: linear-gradient(90deg, #22c55e, #4ade80); }
.card-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.65rem; font-weight: 700; padding: 2px 8px;
  border-radius: 6px; margin-bottom: 12px; letter-spacing: 0.06em; text-transform: uppercase;
}
.cb-red { background: rgba(239,68,68,0.1); color: #f87171 !important; }
.cb-amber { background: rgba(245,158,11,0.1); color: #fbbf24 !important; }
.cb-green { background: rgba(34,197,94,0.1); color: #4ade80 !important; }
.card-type { font-size: 0.65rem; color: #4a5872 !important; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; }
.card-quote {
  font-size: 0.83rem; color: #8b9ab2 !important; font-style: italic;
  line-height: 1.7; margin-bottom: 16px;
  background: oklch(14% 0.007 250); border-radius: 6px; padding: 10px 14px;
}
.card-prob { font-size: 2rem; font-weight: 900; line-height: 1; }
.cp-red { color: #ef4444 !important; }
.cp-amber { color: #f59e0b !important; }
.cp-green { color: #22c55e !important; }
.card-prob-label { font-size: 0.67rem; color: #4a5872 !important; margin-bottom: 14px; }
.card-flags { display: flex; flex-wrap: wrap; gap: 4px; }
.flag {
  font-size: 0.62rem; color: #4a5872 !important;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
  padding: 2px 7px; border-radius: 4px;
}

/* ── Steps ── */
.steps-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; }
.step {
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px; padding: 24px; position: relative;
}
.step-connector {
  position: absolute; top: 38px; right: -8px; width: 16px; height: 1px;
  background: rgba(99,102,241,0.3); display: none;
}
.step-num {
  width: 34px; height: 34px; border-radius: 9px;
  background: rgba(0,148,212,0.10); border: 1px solid rgba(0,148,212,0.28);
  color: #00b8f0 !important; font-size: 0.85rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center; margin-bottom: 14px;
}
.step-t { font-size: 0.9rem; font-weight: 700; color: #e8f0ff !important; margin-bottom: 8px; }
.step-d { font-size: 0.8rem; color: #7a8fa8 !important; line-height: 1.7; }

/* ── Pricing ── */
.pricing-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.plan {
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px; padding: 28px; position: relative;
}
.plan.pop {
  background: rgba(0,148,212,0.05); border-color: rgba(0,148,212,0.35);
  box-shadow: 0 0 40px rgba(0,148,212,0.08);
}
.pop-pill {
  position: absolute; top: -13px; left: 50%; transform: translateX(-50%);
  background: linear-gradient(135deg, #0094d4, #005f8a);
  color: #fff !important; font-size: 0.65rem; font-weight: 700;
  padding: 3px 14px; border-radius: 100px; white-space: nowrap; letter-spacing: 0.06em;
}
.plan-tier { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3a4a5c !important; margin-bottom: 8px; }
.plan-tier.pro { color: #00b8f0 !important; }
.plan-tier.prem { color: #f59e0b !important; }
.plan-price { font-size: 2.4rem; font-weight: 900; color: #e8f0ff !important; letter-spacing: -0.04em; line-height: 1; }
.plan-price sub { font-size: 0.85rem; font-weight: 400; color: #3a4a5c !important; vertical-align: middle; }
.plan-save { font-size: 0.72rem; color: #22c55e !important; margin: 4px 0; min-height: 1.2rem; }
.plan-desc { font-size: 0.8rem; color: #3a4a5c !important; padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 16px; }
.plan-feats { list-style: none; padding: 0; margin: 0; }
.plan-feats li { font-size: 0.82rem; color: #7a8fa8 !important; padding: 5px 0; display: flex; align-items: flex-start; gap: 8px; }
.pf-ck { color: #0094d4 !important; font-weight: 700; flex-shrink: 0; font-size: 0.85rem; }
.pf-cx { color: #253040 !important; flex-shrink: 0; font-size: 0.85rem; }
.pf-dim { color: #253040 !important; }
.pf-pro { color: #00b8f0 !important; font-weight: 500; }
.pf-prem { color: #f59e0b !important; font-weight: 500; }

/* ── Footer ── */
.footer-w { background: #050709; border-top: 1px solid rgba(0,148,212,0.12); padding: 32px 24px; text-align: center; }
.f-logo { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }
.f-logo span { font-size: 0.95rem; font-weight: 800; color: #e8f0ff !important; }
.f-sub { font-size: 0.78rem; color: #253040 !important; margin-bottom: 16px; }
.f-links { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; margin-bottom: 16px; }
.f-links a { color: #3a4a5c !important; font-size: 0.78rem; text-decoration: none; }
.f-copy { font-size: 0.7rem; color: #1a2535 !important; }
</style>"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML blocks
# ─────────────────────────────────────────────────────────────────────────────

_SOCIAL_PROOF = (
    '<div class="sp-bar">'
    '<div class="sp-avatars">'
    '<div class="sp-av" style="background:#0094d4;">JM</div>'
    '<div class="sp-av" style="background:#006fa8;">SR</div>'
    '<div class="sp-av" style="background:#ef4444;">AK</div>'
    '<div class="sp-av" style="background:#f59e0b;">TP</div>'
    '<div class="sp-av" style="background:#22c55e;">DL</div>'
    '<div class="sp-av" style="background:#0ea5e9;">+</div>'
    '</div>'
    '<div class="sp-text"><b>1,247 users</b> caught scams this week &mdash; '
    '&#9733;&#9733;&#9733;&#9733;&#9733; &ldquo;Caught a pig-butchering attempt instantly.&rdquo;</div>'
    '</div>'
)

_HERO = (
    '<div class="hero-wrap">'
    '<div class="hero-glow-l"></div>'
    '<div class="hero-glow-r"></div>'
    '<div class="hero-badge"><span class="badge-pulse"></span>Live Protection &middot; 30+ Detection Patterns</div>'
    '<h1 class="hero-h">The AI That <span class="hero-grad">Sees Through</span><br>Every Scam</h1>'
    '<p class="hero-sub">Paste any email, message, link or phone script. '
    'Get a verdict in under 2 seconds &mdash; before the damage is done.</p>'
    '<div class="hero-trust">'
    '<div class="ht-item"><div class="ht-n">10,847</div><div class="ht-l">Scams caught</div></div>'
    '<div class="ht-item"><div class="ht-n">&lt;2s</div><div class="ht-l">Analysis time</div></div>'
    '<div class="ht-item"><div class="ht-n">30+</div><div class="ht-l">Detection patterns</div></div>'
    '<div class="ht-item"><div class="ht-n">98%</div><div class="ht-l">Accuracy rate</div></div>'
    '</div></div>'
)

_EXAMPLES = (
    '<div class="sec">'
    '<div class="sec-tag">&#128308; Real Scam Cases</div>'
    '<div class="sec-h">We see through them instantly</div>'
    '<p class="sec-s">Real messages caught by ScamSence. Try them yourself &mdash; same result every time.</p>'
    '<div class="cards-grid">'

    '<div class="card red">'
    '<span class="card-badge cb-red">&#9940; SCAM DETECTED</span>'
    '<div class="card-type">Bank / Phishing</div>'
    '<div class="card-quote">&ldquo;Your Chase account has been suspended due to suspicious activity. '
    'Verify your identity immediately: http://chase-secure-verify.xyz/login&rdquo;</div>'
    '<div class="card-prob cp-red">96%</div>'
    '<div class="card-prob-label">scam probability</div>'
    '<div class="card-flags">'
    '<span class="flag">Bank impersonation</span>'
    '<span class="flag">Fake urgency</span>'
    '<span class="flag">Phishing domain</span>'
    '</div></div>'

    '<div class="card amber">'
    '<span class="card-badge cb-amber">&#9888; LIKELY SCAM</span>'
    '<div class="card-type">Investment / Crypto</div>'
    '<div class="card-quote">&ldquo;Hey! I\'ve been trading crypto for 3 years, portfolio up +847% this year. '
    'Let me add you to my private group &mdash; first month free.&rdquo;</div>'
    '<div class="card-prob cp-amber">89%</div>'
    '<div class="card-prob-label">scam probability</div>'
    '<div class="card-flags">'
    '<span class="flag">Pig butchering</span>'
    '<span class="flag">Unrealistic returns</span>'
    '<span class="flag">Crypto scheme</span>'
    '</div></div>'

    '<div class="card red">'
    '<span class="card-badge cb-red">&#9940; SCAM DETECTED</span>'
    '<div class="card-type">Prize / Lottery</div>'
    '<div class="card-quote">&ldquo;Congratulations! You\'ve won a FREE iPhone 15 Pro. '
    'Pay $4.99 shipping to claim. Offer expires in 24 hours!&rdquo;</div>'
    '<div class="card-prob cp-red">97%</div>'
    '<div class="card-prob-label">scam probability</div>'
    '<div class="card-flags">'
    '<span class="flag">Too good to be true</span>'
    '<span class="flag">Fee required</span>'
    '<span class="flag">Fake deadline</span>'
    '</div></div>'

    '</div></div>'
)

_HOW = (
    '<div class="sec" style="padding-top:0;">'
    '<div class="sec-tag">&#9881; How It Works</div>'
    '<div class="sec-h">Three steps to safety</div>'
    '<p class="sec-s">No account. No tracking. Instant analysis.</p>'
    '<div class="steps-grid">'

    '<div class="step"><div class="step-num">01</div>'
    '<div class="step-t">Paste suspicious content</div>'
    '<p class="step-d">Email, SMS, ad, link, phone script &mdash; any format. '
    'Select content type for precision.</p></div>'

    '<div class="step"><div class="step-num">02</div>'
    '<div class="step-t">AI scans in &lt;2 seconds</div>'
    '<p class="step-d">30+ pattern checks: urgency tactics, impersonation, '
    'too-good-to-be-true, suspicious domains.</p></div>'

    '<div class="step"><div class="step-num">03</div>'
    '<div class="step-t">Get a clear verdict</div>'
    '<p class="step-d">Scam / Suspicious / Legitimate with probability score, '
    'red flags, and specific action steps.</p></div>'

    '<div class="step"><div class="step-num">04</div>'
    '<div class="step-t">Stay protected</div>'
    '<p class="step-d">Pro users get full history, PDF reports, and unlimited '
    'checks across all 5 detection modes.</p></div>'

    '</div></div>'
)

_PRICING = (
    '<div class="sec" style="text-align:center;padding-top:0;">'
    '<div class="sec-tag">&#128179; Pricing</div>'
    '<div class="sec-h">Start free, upgrade when ready</div>'
    '<p class="sec-s" style="margin:0 auto 40px;">No credit card required. Cancel anytime.</p>'
    '<div class="pricing-grid">'

    '<div class="plan">'
    '<div class="plan-tier">Free</div>'
    '<div class="plan-price">$0<sub> / mo</sub></div>'
    '<div class="plan-save">&nbsp;</div>'
    '<div class="plan-desc">Perfect for occasional checks</div>'
    '<ul class="plan-feats">'
    '<li><span class="pf-ck">&#10003;</span> 5 checks per day per IP</li>'
    '<li><span class="pf-ck">&#10003;</span> Text &amp; SMS analysis</li>'
    '<li><span class="pf-ck">&#10003;</span> Email check</li>'
    '<li><span class="pf-ck">&#10003;</span> URL analysis</li>'
    '<li><span class="pf-cx">&#10007;</span> <span class="pf-dim">Check history</span></li>'
    '<li><span class="pf-cx">&#10007;</span> <span class="pf-dim">PDF reports</span></li>'
    '<li><span class="pf-cx">&#10007;</span> <span class="pf-dim">Voice analysis</span></li>'
    '</ul></div>'

    '<div class="plan pop">'
    '<div class="pop-pill">&#11088; MOST POPULAR</div>'
    '<div class="plan-tier pro">Pro</div>'
    '<div class="plan-price">$9<sub> / mo</sub></div>'
    '<div class="plan-save">or $7/mo billed annually &mdash; save 22%</div>'
    '<div class="plan-desc">For users who take security seriously</div>'
    '<ul class="plan-feats">'
    '<li><span class="pf-ck">&#10003;</span> Unlimited checks</li>'
    '<li><span class="pf-ck">&#10003;</span> All content types</li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-pro">Full check history</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-pro">PDF reports</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-pro">Priority analysis</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-pro">Browser extension</span> <em style="color:#2d3a52;">(soon)</em></li>'
    '<li><span class="pf-cx">&#10007;</span> <span class="pf-dim">Voice analysis</span></li>'
    '</ul></div>'

    '<div class="plan">'
    '<div class="plan-tier prem">Premium</div>'
    '<div class="plan-price">$19<sub> / mo</sub></div>'
    '<div class="plan-save">or $15/mo annually &mdash; save 21%</div>'
    '<div class="plan-desc">For teams &amp; power users</div>'
    '<ul class="plan-feats">'
    '<li><span class="pf-ck">&#10003;</span> Everything in Pro</li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-prem">Voice analysis (AI)</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-prem">5-seat team access</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-prem">API access</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-prem">YouTube transcript scan</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-prem">Bulk analysis</span></li>'
    '<li><span class="pf-ck">&#10003;</span> <span class="pf-prem">Priority support</span></li>'
    '</ul></div>'

    '</div></div>'
)

_FOOTER = (
    '<div class="footer-w">'
    '<div class="f-logo">'
    '<div style="width:22px;height:22px;border-radius:6px;background:linear-gradient(135deg,#0094d4,#005f8a);'
    'display:flex;align-items:center;justify-content:center;font-size:11px;">&#128737;</div>'
    '<span>ScamSence</span>'
    '</div>'
    '<div class="f-sub">AI-powered Scam &amp; Fraud Detection</div>'
    '<div class="f-links">'
    '<a href="#">About</a><a href="#">API Docs</a>'
    '<a href="#">Privacy</a><a href="#">Terms</a><a href="#">Contact</a>'
    '</div>'
    '<div class="f-copy">&copy; 2026 ScamSence &middot; Built to protect people from fraud</div>'
    '</div>'
)


# ─────────────────────────────────────────────────────────────────────────────
# Render
# ─────────────────────────────────────────────────────────────────────────────

def render() -> None:
    """Renders the ScamSence premium EN landing page."""
    # Remove Streamlit block padding for landing
    st.markdown(
        _CSS + "<style>.block-container{padding-left:0!important;padding-right:0!important;padding-top:0!important;}</style>",
        unsafe_allow_html=True,
    )

    # Social proof bar (above hero)
    st.markdown(_SOCIAL_PROOF, unsafe_allow_html=True)

    # Hero section
    st.markdown(_HERO, unsafe_allow_html=True)

    # CTA buttons
    col_l, col_a, col_b, col_r = st.columns([1.5, 1.2, 1, 2])
    with col_a:
        if st.button("Analyze Now — Free", type="primary",
                     use_container_width=True, key="hero_cta"):
            st.session_state["page_nav"] = "Analyzer"
            st.rerun()
    with col_b:
        st.button("See Examples ↓", use_container_width=True, key="hero_ex")

    # Examples
    st.markdown("<hr class='divl'>", unsafe_allow_html=True)
    st.markdown(_EXAMPLES, unsafe_allow_html=True)
    col_l2, col_c2, col_r2 = st.columns([2, 1.4, 2])
    with col_c2:
        if st.button("Try it yourself →", use_container_width=True, key="try_cta"):
            st.session_state["page_nav"] = "Analyzer"
            st.rerun()

    # How it works
    st.markdown("<hr class='divl'>", unsafe_allow_html=True)
    st.markdown(_HOW, unsafe_allow_html=True)

    # Pricing
    st.markdown("<hr class='divl'>", unsafe_allow_html=True)
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
    st.markdown("<hr class='divl'>", unsafe_allow_html=True)
    st.markdown(_FOOTER, unsafe_allow_html=True)
