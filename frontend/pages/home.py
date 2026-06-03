"""
frontend/pages/home.py - Landing Page ScamSence

Design: Professional Dark (#0f1117, indigo #5865f2, red #ff3b3b)
Sections: Hero -> Examples -> How it works -> Pricing -> Footer
"""
import streamlit as st

# CSS stored as separate parts to avoid truncation issues
_CSS_PART1 = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');"
    "* { font-family: 'Inter', sans-serif !important; }"
    ".block-container { padding-top: 0 !important; max-width: 100% !important; }"
)

_CSS_PART2 = (
    ".hero {"
    "background: linear-gradient(160deg, #0d0f1a 0%, #12152b 50%, #0d0f1a 100%);"
    "padding: 72px 24px 56px; text-align: center;"
    "border-bottom: 1px solid #1c2040; position: relative; overflow: hidden;}"
    ".hero::before {content: ''; position: absolute; top: -100px; left: 50%;"
    "transform: translateX(-50%); width: 700px; height: 700px;"
    "background: radial-gradient(circle, rgba(88,101,242,0.12) 0%, transparent 65%);"
    "pointer-events: none;}"
    ".hero-badge {display: inline-block; background: rgba(88,101,242,0.12);"
    "border: 1px solid rgba(88,101,242,0.35); color: #a5b4fc;"
    "font-size: 0.75rem; font-weight: 700; padding: 4px 14px; border-radius: 100px;"
    "letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 22px;}"
    ".hero-title {font-size: clamp(2rem,4vw,3.1rem); font-weight: 900; line-height: 1.15;"
    "color: #ffffff; margin: 0 0 18px; letter-spacing: -0.03em;}"
    ".hero-title .red {background: linear-gradient(135deg, #ff3b3b 30%, #ff7070);"
    "-webkit-background-clip: text; -webkit-text-fill-color: transparent;}"
    ".hero-sub {font-size: 1.05rem; color: #8892aa; max-width: 540px;"
    "margin: 0 auto 36px; line-height: 1.75;}"
    ".hero-stats {display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;"
    "margin-top: 40px; padding-top: 28px; border-top: 1px solid #1c2040;}"
    ".stat {text-align: center;}"
    ".stat-n {font-size: 1.7rem; font-weight: 800; color: #5865f2;}"
    ".stat-l {font-size: 0.76rem; color: #5a6380; margin-top: 2px;}"
)

_CSS_PART3 = (
    ".sec {max-width: 1080px; margin: 0 auto; padding: 60px 24px;}"
    ".sec-label {font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;"
    "text-transform: uppercase; color: #5865f2; margin-bottom: 10px;}"
    ".sec-title {font-size: 1.9rem; font-weight: 800; color: #fff;"
    "margin: 0 0 10px; letter-spacing: -0.02em;}"
    ".sec-sub {color: #8892aa; font-size: 0.95rem; margin-bottom: 36px;}"
    ".divider {border: none; border-top: 1px solid #1c2040; margin: 0;}"
    ".cases {display: grid; grid-template-columns: repeat(3,1fr); gap: 14px;}"
    ".case-card {background: #131627; border: 1px solid #1c2040; border-radius: 14px;"
    "padding: 20px; position: relative; overflow: hidden;}"
    ".case-card::before {content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;}"
    ".case-card.red::before {background: linear-gradient(90deg,#ff3b3b,#ff7070);}"
    ".case-card.amber::before {background: linear-gradient(90deg,#f59e0b,#fbbf24);}"
    ".vbadge {display: inline-flex; align-items: center; gap: 4px;"
    "font-size: 0.7rem; font-weight: 700; padding: 3px 9px; border-radius: 6px;"
    "margin-bottom: 10px; letter-spacing: 0.05em; text-transform: uppercase;}"
    ".vbadge.red {background: rgba(255,59,59,0.14); color: #ff6b6b;}"
    ".vbadge.amber {background: rgba(245,158,11,0.14); color: #fbbf24;}"
    ".ctype {font-size: 0.68rem; color: #5a6380; text-transform: uppercase;"
    "letter-spacing: 0.08em; margin-bottom: 9px;}"
    ".ctext {font-size: 0.85rem; color: #c8cdd8; line-height: 1.65;"
    "font-style: italic; margin-bottom: 14px;"
    "border-left: 2px solid #1c2040; padding-left: 10px;}"
    ".prob {font-size: 2rem; font-weight: 900;}"
    ".prob.red {color: #ff3b3b;}"
    ".prob.amber {color: #f59e0b;}"
    ".prob-label {font-size: 0.72rem; color: #5a6380; margin-bottom: 12px;}"
    ".flags {display: flex; flex-wrap: wrap; gap: 5px;}"
    ".flag {background: rgba(255,255,255,0.04); border: 1px solid #232840;"
    "color: #7a8198; font-size: 0.66rem; padding: 2px 7px; border-radius: 4px;}"
)

_CSS_PART4 = (
    ".steps {display: grid; grid-template-columns: repeat(3,1fr); gap: 20px;}"
    ".step-card {background: #131627; border: 1px solid #1c2040; border-radius: 14px; padding: 26px;}"
    ".step-n {width: 38px; height: 38px; border-radius: 10px;"
    "background: linear-gradient(135deg,#5865f2,#4752c4);"
    "display: flex; align-items: center; justify-content: center;"
    "font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 14px;}"
    ".step-t {font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 7px;}"
    ".step-d {font-size: 0.84rem; color: #8892aa; line-height: 1.65;}"
    ".pricing {display: grid; grid-template-columns: 1fr 1fr; gap: 18px;"
    "max-width: 660px; margin: 0 auto;}"
    ".pcard {background: #131627; border: 1px solid #1c2040; border-radius: 16px; padding: 28px;}"
    ".pcard.featured {background: linear-gradient(145deg,#161a38,#1a1f42);"
    "border-color: #5865f2; position: relative;}"
    ".pop-badge {position: absolute; top: -12px; left: 50%; transform: translateX(-50%);"
    "background: linear-gradient(135deg,#5865f2,#4752c4); color: #fff;"
    "font-size: 0.69rem; font-weight: 700; padding: 3px 12px; border-radius: 100px;"
    "letter-spacing: 0.06em; white-space: nowrap;}"
    ".ptier {font-size: 0.75rem; font-weight: 700; text-transform: uppercase;"
    "letter-spacing: 0.08em; color: #5a6380; margin-bottom: 6px;}"
    ".ptier.pro {color: #a5b4fc;}"
    ".pprice {font-size: 2.2rem; font-weight: 900; color: #fff; margin-bottom: 3px;}"
    ".pprice .per {font-size: 0.9rem; font-weight: 400; color: #5a6380;}"
    ".pdesc {font-size: 0.82rem; color: #8892aa; margin-bottom: 20px;"
    "padding-bottom: 18px; border-bottom: 1px solid #1c2040;}"
    ".pfeats {list-style: none; padding: 0; margin: 0;}"
    ".pfeats li {font-size: 0.85rem; color: #c5cae9; padding: 5px 0;"
    "display: flex; align-items: flex-start; gap: 7px;}"
    ".ck {color: #5865f2; font-weight: 700; flex-shrink: 0;}"
    ".cx {color: #3a3f5c; flex-shrink: 0;}"
    ".dim {color: #3a3f5c;}"
    ".pro-feat {color: #a5b4fc; font-weight: 600;}"
    ".footer {background: #090b14; border-top: 1px solid #1c2040;"
    "padding: 28px 24px; text-align: center;}"
    ".footer-logo {font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 6px;}"
    ".footer-tagline {color: #5a6380; font-size: 0.82rem; margin-bottom: 14px;}"
    ".footer-links {display: flex; justify-content: center; gap: 20px;"
    "flex-wrap: wrap; margin-bottom: 14px;}"
    ".footer-links a {color: #5a6380; font-size: 0.8rem; text-decoration: none;}"
    ".footer-links a:hover {color: #a5b4fc;}"
    ".footer-copy {color: #3a3f5c; font-size: 0.74rem;}"
    "</style>"
)

_LANDING_CSS = _CSS_PART1 + _CSS_PART2 + _CSS_PART3 + _CSS_PART4

_HERO_HTML = (
    '<div class="hero">'
    '<div class="hero-badge">&#128737; AI-Powered &middot; 2026</div>'
    '<h1 class="hero-title">ScamSence &mdash; AI, который<br>'
    '<span class="red">&#1079;&#1072;&#1097;&#1080;&#1097;&#1072;&#1077;&#1090; &#1090;&#1077;&#1073;&#1103;</span> &#1086;&#1090; &#1084;&#1086;&#1096;&#1077;&#1085;&#1085;&#1080;&#1082;&#1086;&#1074;</h1>'
    '<p class="hero-sub">&#1042;&#1089;&#1090;&#1072;&#1074;&#1100; &#1089;&#1086;&#1086;&#1073;&#1097;&#1077;&#1085;&#1080;&#1077;, email &#1080;&#1083;&#1080; &#1089;&#1089;&#1099;&#1083;&#1082;&#1091; &mdash; &#1079;&#1072; 2 &#1089;&#1077;&#1082;&#1091;&#1085;&#1076;&#1099; &#1087;&#1086;&#1083;&#1091;&#1095;&#1080;&#1096;&#1100; &#1074;&#1077;&#1088;&#1076;&#1080;&#1082;&#1090;. 30+ &#1087;&#1072;&#1090;&#1090;&#1077;&#1088;&#1085;&#1086;&#1074; &#1088;&#1072;&#1089;&#1087;&#1086;&#1079;&#1085;&#1072;&#1074;&#1072;&#1085;&#1080;&#1103;, &#1073;&#1072;&#1079;&#1072; &#1088;&#1077;&#1072;&#1083;&#1100;&#1085;&#1099;&#1093; &#1089;&#1082;&#1072;&#1084;-&#1082;&#1077;&#1081;&#1089;&#1086;&#1074;.</p>'
    '<div class="hero-stats">'
    '<div class="stat"><div class="stat-n">30+</div><div class="stat-l">&#1055;&#1072;&#1090;&#1090;&#1077;&#1088;&#1085;&#1086;&#1074;</div></div>'
    '<div class="stat"><div class="stat-n">5</div><div class="stat-l">&#1058;&#1080;&#1087;&#1086;&#1074; &#1087;&#1088;&#1086;&#1074;&#1077;&#1088;&#1086;&#1082;</div></div>'
    '<div class="stat"><div class="stat-n">2 &#1089;&#1077;&#1082;</div><div class="stat-l">&#1042;&#1088;&#1077;&#1084;&#1103; &#1072;&#1085;&#1072;&#1083;&#1080;&#1079;&#1072;</div></div>'
    '<div class="stat"><div class="stat-n">Free</div><div class="stat-l">&#1053;&#1072;&#1095;&#1085;&#1080; &#1089;&#1077;&#1081;&#1095;&#1072;&#1089;</div></div>'
    '</div></div>'
)

_CASES_HTML = (
    '<div class="sec">'
    '<div class="sec-label">&#128308; &#1055;&#1088;&#1080;&#1084;&#1077;&#1088;&#1099; &#1088;&#1072;&#1079;&#1073;&#1086;&#1088;&#1086;&#1074;</div>'
    '<div class="sec-title">&#1042;&#1080;&#1076;&#1080;&#1084; &#1084;&#1086;&#1096;&#1077;&#1085;&#1085;&#1080;&#1082;&#1086;&#1074; &#1085;&#1072;&#1089;&#1082;&#1074;&#1086;&#1079;&#1100;</div>'
    '<p class="sec-sub">&#1056;&#1077;&#1072;&#1083;&#1100;&#1085;&#1099;&#1077; &#1089;&#1082;&#1072;&#1084;-&#1089;&#1086;&#1086;&#1073;&#1097;&#1077;&#1085;&#1080;&#1103; &mdash; &#1085;&#1072;&#1078;&#1084;&#1080; &laquo;&#1055;&#1088;&#1086;&#1074;&#1077;&#1088;&#1080;&#1090;&#1100;&raquo;, &#1087;&#1086;&#1083;&#1091;&#1095;&#1080;&#1096;&#1100; &#1090;&#1086;&#1090; &#1078;&#1077; &#1088;&#1077;&#1079;&#1091;&#1083;&#1100;&#1090;&#1072;&#1090;.</p>'
    '<div class="cases">'

    '<div class="case-card red">'
    '<span class="vbadge red">&#9940; SCAM</span>'
    '<div class="ctype">&#1051;&#1086;&#1090;&#1077;&#1088;&#1077;&#1103; / &#1055;&#1088;&#1080;&#1079;</div>'
    '<div class="ctext">&ldquo;Congratulations! You\'ve been selected to receive an Apple iPhone 15 Pro. '
    'To claim your prize, click the link and pay $4.99 shipping fee.&rdquo;</div>'
    '<div class="prob red">97%</div>'
    '<div class="prob-label">&#1074;&#1077;&#1088;&#1086;&#1103;&#1090;&#1085;&#1086;&#1089;&#1090;&#1100; &#1089;&#1082;&#1072;&#1084;&#1072;</div>'
    '<div class="flags">'
    '<span class="flag">&#127873; Too Good To Be True</span>'
    '<span class="flag">&#128179; Fee required</span>'
    '<span class="flag">&#128279; Suspicious link</span>'
    '</div></div>'

    '<div class="case-card red">'
    '<span class="vbadge red">&#9940; SCAM</span>'
    '<div class="ctype">&#1041;&#1072;&#1085;&#1082; / &#1060;&#1080;&#1096;&#1080;&#1085;&#1075;</div>'
    '<div class="ctext">&ldquo;&#1042;&#1072;&#1096; &#1072;&#1082;&#1082;&#1072;&#1091;&#1085;&#1090; &#1057;&#1073;&#1077;&#1088;&#1073;&#1072;&#1085;&#1082; &#1079;&#1072;&#1073;&#1083;&#1086;&#1082;&#1080;&#1088;&#1086;&#1074;&#1072;&#1085;. '
    '&#1057;&#1088;&#1086;&#1095;&#1085;&#1086; &#1087;&#1086;&#1076;&#1090;&#1074;&#1077;&#1088;&#1076;&#1080;&#1090;&#1077; &#1076;&#1072;&#1085;&#1085;&#1099;&#1077; &#1087;&#1086; &#1089;&#1089;&#1099;&#1083;&#1082;&#1077; &#1074; &#1090;&#1077;&#1095;&#1077;&#1085;&#1080;&#1077; 24 &#1095;&#1072;&#1089;&#1086;&#1074;.&rdquo;</div>'
    '<div class="prob red">94%</div>'
    '<div class="prob-label">&#1074;&#1077;&#1088;&#1086;&#1103;&#1090;&#1085;&#1086;&#1089;&#1090;&#1100; &#1089;&#1082;&#1072;&#1084;&#1072;</div>'
    '<div class="flags">'
    '<span class="flag">&#127970; Bank impersonation</span>'
    '<span class="flag">&#9200; Urgency pressure</span>'
    '<span class="flag">&#128279; Phishing link</span>'
    '</div></div>'

    '<div class="case-card amber">'
    '<span class="vbadge amber">&#9888; LIKELY SCAM</span>'
    '<div class="ctype">&#1048;&#1085;&#1074;&#1077;&#1089;&#1090;&#1080;&#1094;&#1080;&#1080; / &#1050;&#1088;&#1080;&#1087;&#1090;&#1086;</div>'
    '<div class="ctext">&ldquo;&#1055;&#1088;&#1080;&#1074;&#1077;&#1090;! &#1071; &#1090;&#1086;&#1088;&#1075;&#1091;&#1102; &#1082;&#1088;&#1080;&#1087;&#1090;&#1086; 3 &#1075;&#1086;&#1076;&#1072;, &#1087;&#1086;&#1088;&#1090;&#1092;&#1077;&#1083;&#1100; +847% &#1079;&#1072; &#1075;&#1086;&#1076;. '
    '&#1052;&#1086;&#1075;&#1091; &#1076;&#1086;&#1073;&#1072;&#1074;&#1080;&#1090;&#1100; &#1090;&#1077;&#1073;&#1103; &#1074; &#1079;&#1072;&#1082;&#1088;&#1099;&#1090;&#1091;&#1102; &#1075;&#1088;&#1091;&#1087;&#1087;&#1091; &mdash; &#1087;&#1077;&#1088;&#1074;&#1099;&#1081; &#1084;&#1077;&#1089;&#1103;&#1094; &#1073;&#1077;&#1089;&#1087;&#1083;&#1072;&#1090;&#1085;&#1086;.&rdquo;</div>'
    '<div class="prob amber">89%</div>'
    '<div class="prob-label">&#1074;&#1077;&#1088;&#1086;&#1103;&#1090;&#1085;&#1086;&#1089;&#1090;&#1100; &#1089;&#1082;&#1072;&#1084;&#1072;</div>'
    '<div class="flags">'
    '<span class="flag">&#128176; Unrealistic returns</span>'
    '<span class="flag">&#128055; Pig butchering</span>'
    '<span class="flag">&#128202; Crypto scheme</span>'
    '</div></div>'

    '</div></div>'
)

_HOW_HTML = (
    '<div class="sec">'
    '<div class="sec-label">&#9881; &#1050;&#1072;&#1082; &#1101;&#1090;&#1086; &#1088;&#1072;&#1073;&#1086;&#1090;&#1072;&#1077;&#1090;</div>'
    '<div class="sec-title">&#1058;&#1088;&#1080; &#1096;&#1072;&#1075;&#1072; &mdash; &#1080; &#1090;&#1099; &#1074; &#1073;&#1077;&#1079;&#1086;&#1087;&#1072;&#1089;&#1085;&#1086;&#1089;&#1090;&#1080;</div>'
    '<p class="sec-sub">&#1041;&#1077;&#1079; &#1088;&#1077;&#1075;&#1080;&#1089;&#1090;&#1088;&#1072;&#1094;&#1080;&#1080;. &#1041;&#1077;&#1079; &#1089;&#1083;&#1077;&#1078;&#1082;&#1080;. &#1055;&#1088;&#1086;&#1089;&#1090;&#1086; &#1074;&#1089;&#1090;&#1072;&#1074;&#1100; &#1090;&#1077;&#1082;&#1089;&#1090; &mdash; &#1087;&#1086;&#1083;&#1091;&#1095;&#1080; &#1086;&#1090;&#1074;&#1077;&#1090;.</p>'
    '<div class="steps">'
    '<div class="step-card"><div class="step-n">1</div>'
    '<div class="step-t">&#1042;&#1089;&#1090;&#1072;&#1074;&#1100; &#1087;&#1086;&#1076;&#1086;&#1079;&#1088;&#1080;&#1090;&#1077;&#1083;&#1100;&#1085;&#1099;&#1081; &#1090;&#1077;&#1082;&#1089;&#1090;</div>'
    '<p class="step-d">SMS, &#1087;&#1080;&#1089;&#1100;&#1084;&#1086;, &#1086;&#1073;&#1098;&#1103;&#1074;&#1083;&#1077;&#1085;&#1080;&#1077;, &#1089;&#1089;&#1099;&#1083;&#1082;&#1072;, &#1090;&#1077;&#1083;&#1077;&#1092;&#1086;&#1085;&#1085;&#1099;&#1081; &#1089;&#1082;&#1088;&#1080;&#1087;&#1090; &mdash; '
    '&#1083;&#1102;&#1073;&#1086;&#1081; &#1092;&#1086;&#1088;&#1084;&#1072;&#1090;. &#1042;&#1099;&#1073;&#1077;&#1088;&#1080; &#1090;&#1080;&#1087; &#1082;&#1086;&#1085;&#1090;&#1077;&#1085;&#1090;&#1072; &#1076;&#1083;&#1103; &#1090;&#1086;&#1095;&#1085;&#1077;&#1077; &#1072;&#1085;&#1072;&#1083;&#1080;&#1079;&#1072;.</p></div>'
    '<div class="step-card"><div class="step-n">2</div>'
    '<div class="step-t">AI &#1072;&#1085;&#1072;&#1083;&#1080;&#1079;&#1080;&#1088;&#1091;&#1077;&#1090; &#1079;&#1072; 2 &#1089;&#1077;&#1082;&#1091;&#1085;&#1076;&#1099;</div>'
    '<p class="step-d">30+ &#1087;&#1072;&#1090;&#1090;&#1077;&#1088;&#1085;&#1086;&#1074;: &#1089;&#1088;&#1086;&#1095;&#1085;&#1086;&#1089;&#1090;&#1100;, impersonation, '
    '&#1089;&#1083;&#1080;&#1096;&#1082;&#1086;&#1084; &#1093;&#1086;&#1088;&#1086;&#1096;&#1086; &#1095;&#1090;&#1086;&#1073;&#1099; &#1073;&#1099;&#1090;&#1100; &#1087;&#1088;&#1072;&#1074;&#1076;&#1086;&#1081;, &#1087;&#1086;&#1076;&#1086;&#1079;&#1088;&#1080;&#1090;&#1077;&#1083;&#1100;&#1085;&#1099;&#1077; &#1089;&#1089;&#1099;&#1083;&#1082;&#1080;.</p></div>'
    '<div class="step-card"><div class="step-n">3</div>'
    '<div class="step-t">&#1055;&#1086;&#1083;&#1091;&#1095;&#1080; &#1074;&#1077;&#1088;&#1076;&#1080;&#1082;&#1090; &#1080; &#1086;&#1073;&#1098;&#1103;&#1089;&#1085;&#1077;&#1085;&#1080;&#1077;</div>'
    '<p class="step-d">&#1063;&#1077;&#1090;&#1082;&#1080;&#1081; &#1074;&#1077;&#1088;&#1076;&#1080;&#1082;&#1090; (Scam / Suspicious / Legitimate), '
    '&#1082;&#1088;&#1072;&#1089;&#1085;&#1099;&#1077; &#1092;&#1083;&#1072;&#1075;&#1080; &#1089; severity &#1080; &#1088;&#1077;&#1082;&#1086;&#1084;&#1077;&#1085;&#1076;&#1072;&#1094;&#1080;&#1080; &#1095;&#1090;&#1086; &#1076;&#1077;&#1083;&#1072;&#1090;&#1100; &#1076;&#1072;&#1083;&#1100;&#1096;&#1077;.</p></div>'
    '</div></div>'
)

_PRICING_HTML = (
    '<div class="sec" style="text-align:center;">'
    '<div class="sec-label">&#128179; &#1058;&#1072;&#1088;&#1080;&#1092;&#1099;</div>'
    '<div class="sec-title">&#1053;&#1072;&#1095;&#1085;&#1080; &#1073;&#1077;&#1089;&#1087;&#1083;&#1072;&#1090;&#1085;&#1086;</div>'
    '<p class="sec-sub" style="margin:0 auto 36px;">&#1041;&#1077;&#1089;&#1087;&#1083;&#1072;&#1090;&#1085;&#1086;&#1075;&#1086; &#1087;&#1083;&#1072;&#1085;&#1072; &#1093;&#1074;&#1072;&#1090;&#1072;&#1077;&#1090; &#1076;&#1083;&#1103; &#1083;&#1080;&#1095;&#1085;&#1086;&#1075;&#1086; &#1080;&#1089;&#1087;&#1086;&#1083;&#1100;&#1079;&#1086;&#1074;&#1072;&#1085;&#1080;&#1103;. Pro &mdash; &#1076;&#1083;&#1103; &#1073;&#1080;&#1079;&#1085;&#1077;&#1089;&#1072;.</p>'
    '<div class="pricing">'

    '<div class="pcard">'
    '<div class="ptier">Free</div>'
    '<div class="pprice">$0 <span class="per">/ &#1084;&#1077;&#1089;&#1103;&#1094;</span></div>'
    '<div class="pdesc">&#1042;&#1089;&#1105; &#1095;&#1090;&#1086; &#1085;&#1091;&#1078;&#1085;&#1086; &#1076;&#1083;&#1103; &#1085;&#1072;&#1095;&#1072;&#1083;&#1072;</div>'
    '<ul class="pfeats">'
    '<li><span class="ck">&#10003;</span> 5 &#1087;&#1088;&#1086;&#1074;&#1077;&#1088;&#1086;&#1082; &#1074; &#1076;&#1077;&#1085;&#1100;</li>'
    '<li><span class="ck">&#10003;</span> &#1040;&#1085;&#1072;&#1083;&#1080;&#1079; &#1090;&#1077;&#1082;&#1089;&#1090;&#1072; &#1080; SMS</li>'
    '<li><span class="ck">&#10003;</span> Email &#1087;&#1088;&#1086;&#1074;&#1077;&#1088;&#1082;&#1072;</li>'
    '<li><span class="ck">&#10003;</span> &#1041;&#1072;&#1079;&#1086;&#1074;&#1099;&#1077; &#1082;&#1088;&#1072;&#1089;&#1085;&#1099;&#1077; &#1092;&#1083;&#1072;&#1075;&#1080;</li>'
    '<li><span class="cx">&#10007;</span> <span class="dim">URL &#1072;&#1085;&#1072;&#1083;&#1080;&#1079; &#1076;&#1086;&#1084;&#1077;&#1085;&#1072;</span></li>'
    '<li><span class="cx">&#10007;</span> <span class="dim">&#1043;&#1086;&#1083;&#1086;&#1089;&#1086;&#1074;&#1086;&#1081; &#1072;&#1085;&#1072;&#1083;&#1080;&#1079;</span></li>'
    '<li><span class="cx">&#10007;</span> <span class="dim">&#1048;&#1089;&#1090;&#1086;&#1088;&#1080;&#1103; &amp; API</span></li>'
    '</ul></div>'

    '<div class="pcard featured">'
    '<div class="pop-badge">&#11088; POPULAR</div>'
    '<div class="ptier pro">Pro</div>'
    '<div class="pprice">$9 <span class="per">/ &#1084;&#1077;&#1089;&#1103;&#1094;</span></div>'
    '<div class="pdesc">&#1044;&#1083;&#1103; &#1089;&#1077;&#1088;&#1100;&#1105;&#1079;&#1085;&#1086;&#1081; &#1079;&#1072;&#1097;&#1080;&#1090;&#1099;</div>'
    '<ul class="pfeats">'
    '<li><span class="ck">&#10003;</span> &#1041;&#1077;&#1079;&#1083;&#1080;&#1084;&#1080;&#1090;&#1085;&#1099;&#1077; &#1087;&#1088;&#1086;&#1074;&#1077;&#1088;&#1082;&#1080;</li>'
    '<li><span class="ck">&#10003;</span> &#1040;&#1085;&#1072;&#1083;&#1080;&#1079; &#1090;&#1077;&#1082;&#1089;&#1090;&#1072; &#1080; SMS</li>'
    '<li><span class="ck">&#10003;</span> Email + &#1079;&#1072;&#1075;&#1086;&#1083;&#1086;&#1074;&#1082;&#1080; &#1087;&#1080;&#1089;&#1100;&#1084;&#1072;</li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-feat">URL &#1072;&#1085;&#1072;&#1083;&#1080;&#1079; &#1076;&#1086;&#1084;&#1077;&#1085;&#1072;</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-feat">&#1043;&#1086;&#1083;&#1086;&#1089;&#1086;&#1074;&#1086;&#1081; &#1072;&#1085;&#1072;&#1083;&#1080;&#1079; (Whisper)</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-feat">&#1048;&#1089;&#1090;&#1086;&#1088;&#1080;&#1103; &#1087;&#1088;&#1086;&#1074;&#1077;&#1088;&#1086;&#1082;</span></li>'
    '<li><span class="ck">&#10003;</span> <span class="pro-feat">API &#1076;&#1086;&#1089;&#1090;&#1091;&#1087;</span></li>'
    '</ul></div>'

    '</div></div>'
)

_FOOTER_HTML = (
    '<div class="footer">'
    '<div class="footer-logo">&#128737; ScamSence</div>'
    '<div class="footer-tagline">AI-powered Scam &amp; Fraud Detector</div>'
    '<div class="footer-links">'
    '<a href="#">&#1054; &#1087;&#1088;&#1086;&#1077;&#1082;&#1090;&#1077;</a>'
    '<a href="#">API</a>'
    '<a href="#">&#1055;&#1086;&#1083;&#1080;&#1090;&#1080;&#1082;&#1072; &#1082;&#1086;&#1085;&#1092;&#1080;&#1076;&#1077;&#1085;&#1094;&#1080;&#1072;&#1083;&#1100;&#1085;&#1086;&#1089;&#1090;&#1080;</a>'
    '<a href="#">&#1050;&#1086;&#1085;&#1090;&#1072;&#1082;&#1090;&#1099;</a>'
    '</div>'
    '<div class="footer-copy">&copy; 2026 ScamSence &middot; &#1057;&#1076;&#1077;&#1083;&#1072;&#1085;&#1086; &#1076;&#1083;&#1103; &#1079;&#1072;&#1097;&#1080;&#1090;&#1099; &#1083;&#1102;&#1076;&#1077;&#1081; &#1086;&#1090; &#1084;&#1086;&#1096;&#1077;&#1085;&#1085;&#1080;&#1082;&#1086;&#1074;</div>'
    '</div>'
)


def render() -> None:
    """Renders the ScamSence professional landing page."""

    st.markdown(_LANDING_CSS, unsafe_allow_html=True)

    # Hero section
    st.markdown(_HERO_HTML, unsafe_allow_html=True)

    # Functional CTA button (Streamlit handles navigation)
    col_l, col_c, col_r = st.columns([2, 1.6, 2])
    with col_c:
        if st.button(
            "\U0001f50d Проверить на Scam — бесплатно",
            type="primary",
            use_container_width=True,
            key="hero_cta",
        ):
            st.session_state["_nav"] = "\U0001f4ac Text Check"
            st.rerun()

    # Scam examples
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_CASES_HTML, unsafe_allow_html=True)
    col_l2, col_c2, col_r2 = st.columns([2, 1.4, 2])
    with col_c2:
        if st.button(
            "Попробовать самому →",
            use_container_width=True,
            key="cases_cta",
        ):
            st.session_state["_nav"] = "\U0001f4ac Text Check"
            st.rerun()

    # How it works
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_HOW_HTML, unsafe_allow_html=True)

    # Pricing
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_PRICING_HTML, unsafe_allow_html=True)

    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([1.2, 1, 0.4, 1, 1.2])
    with col_f2:
        st.button(
            "Начать бесплатно",
            use_container_width=True,
            key="free_plan",
        )
    with col_f4:
        if st.button(
            "Попробовать Pro →",
            type="primary",
            use_container_width=True,
            key="pro_plan",
        ):
            st.session_state["_nav"] = "\U0001f4ac Text Check"
            st.rerun()

    # Footer
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(_FOOTER_HTML, unsafe_allow_html=True)
