"""
frontend/pages/home.py — Главная страница ScamSence
"""
import streamlit as st


def render() -> None:
    st.title("🛡️ ScamSence")
    st.markdown("### AI-powered Scam & Fraud Detector")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 💬 Text Check
        Analyze any text message, SMS,
        chat, or phone script for scam patterns.
        """)
        if st.button("Check Text →", key="btn_text", use_container_width=True):
            st.session_state["_nav"] = "💬 Text Check"
            st.rerun()

    with col2:
        st.markdown("""
        #### 📧 Email Check
        *(Coming Day 6)*
        Paste full email content to detect
        phishing and impersonation.
        """)
        st.button("Coming soon", key="btn_email", disabled=True, use_container_width=True)

    with col3:
        st.markdown("""
        #### 🔗 URL Check
        *(Coming Day 6)*
        Check suspicious links for
        typosquatting and phishing domains.
        """)
        st.button("Coming soon", key="btn_url", disabled=True, use_container_width=True)

    st.markdown("---")

    st.markdown("### 🔴 10 Scam Patterns We Detect")
    patterns = [
        ("🏛️", "Government Impersonation", "IRS, FBI, Social Security"),
        ("🏦", "Bank Phishing", "Sberbank, PayPal, account threats"),
        ("💰", "Investment Scams", "Guaranteed returns, crypto groups"),
        ("💔", "Romance Scams", "Airport emergency, money requests"),
        ("🎁", "Prize / Lottery", "Fake winners, shipping fee tricks"),
        ("🐷", "Pig Butchering", "Long warm-up + crypto investment"),
        ("👨‍💻", "Tech Support", "Microsoft/Apple fake support"),
        ("💳", "Payment Red Flags", "Gift cards, Bitcoin, wire transfers"),
        ("📋", "Data Harvesting", "SSN, passwords, card numbers"),
        ("🔗", "Suspicious Links", "Typosquatting, URL shorteners"),
    ]
    cols = st.columns(2)
    for i, (emoji, name, desc) in enumerate(patterns):
        with cols[i % 2]:
            st.markdown(f"**{emoji} {name}** — {desc}")

    st.markdown("---")
    st.caption("Backend: http://127.0.0.1:8000/docs · Model: mock-analyzer-v2 · KB: 29 examples")
