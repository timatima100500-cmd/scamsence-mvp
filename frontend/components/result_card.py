"""
frontend/components/result_card.py — Карточка результата анализа

Цвет зависит от вердикта: красный=Scam, оранжевый=Likely Scam,
жёлтый=Suspicious, зелёный=Legitimate.
"""
import streamlit as st


# ── Цветовая схема по вердикту ───────────────────────────────────────────────
_VERDICT_CONFIG = {
    "Scam": {
        "color": "#FF4B4B",
        "bg": "#FFF0F0",
        "border": "#FF4B4B",
        "emoji": "🚨",
        "label": "SCAM",
    },
    "Likely Scam": {
        "color": "#FF8C00",
        "bg": "#FFF5E6",
        "border": "#FF8C00",
        "emoji": "⚠️",
        "label": "LIKELY SCAM",
    },
    "Suspicious": {
        "color": "#D4AC0D",
        "bg": "#FFFDE6",
        "border": "#D4AC0D",
        "emoji": "🔍",
        "label": "SUSPICIOUS",
    },
    "Legitimate": {
        "color": "#00A651",
        "bg": "#F0FFF4",
        "border": "#00A651",
        "emoji": "✅",
        "label": "LEGITIMATE",
    },
}


def render_result_card(response: dict) -> None:
    """
    Отображает карточку результата анализа.

    Args:
        response: dict с полями verdict, probability, red_flags,
                  explanation, recommendations, similar_cases, model_used, analysis_time_ms
    """
    verdict = response.get("verdict", "Unknown")
    probability = response.get("probability", 0)
    red_flags = response.get("red_flags", [])
    explanation = response.get("explanation", "")
    recommendations = response.get("recommendations", [])
    similar_cases = response.get("similar_cases", [])
    model_used = response.get("model_used", "unknown")
    analysis_time_ms = response.get("analysis_time_ms", 0)

    cfg = _VERDICT_CONFIG.get(verdict, _VERDICT_CONFIG["Suspicious"])

    # ── Главный блок вердикта ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        background: {cfg["bg"]};
        border: 2px solid {cfg["border"]};
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 2rem">{cfg["emoji"]}</span>
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {cfg["color"]}">
                    {cfg["label"]}
                </div>
                <div style="color: #666; font-size: 0.9rem">
                    Fraud probability: <strong>{probability}%</strong>
                    &nbsp;·&nbsp; {model_used}
                    &nbsp;·&nbsp; {analysis_time_ms}ms
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Прогресс-бар ────────────────────────────────────────────────────────
    st.progress(probability / 100)

    # ── Red Flags ────────────────────────────────────────────────────────────
    if red_flags:
        st.markdown("### 🚩 Red Flags Detected")
        for flag in red_flags:
            severity = flag.get("severity", 5)
            # Цвет по severity: 1-3=green, 4-6=orange, 7-10=red
            if severity >= 7:
                badge_color = "#FF4B4B"
            elif severity >= 4:
                badge_color = "#FF8C00"
            else:
                badge_color = "#D4AC0D"

            st.markdown(f"""
            <div style="
                display: flex; align-items: center; gap: 8px;
                padding: 6px 0; border-bottom: 1px solid #eee;
            ">
                <span style="
                    background: {badge_color}; color: white;
                    padding: 2px 8px; border-radius: 12px;
                    font-size: 0.75rem; font-weight: 600;
                    min-width: 24px; text-align: center;
                ">{severity}</span>
                <span style="color: #333">{flag.get("description", "")}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("")
    else:
        st.info("No red flags detected.")

    # ── Объяснение ───────────────────────────────────────────────────────────
    if explanation:
        st.markdown("### 💬 Explanation")
        st.markdown(f"> {explanation}")

    # ── Рекомендации ─────────────────────────────────────────────────────────
    if recommendations:
        st.markdown("### 📋 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")

    # ── Похожие кейсы из KB ──────────────────────────────────────────────────
    if similar_cases:
        with st.expander(f"🔎 Similar known cases ({len(similar_cases)} found)", expanded=False):
            for case in similar_cases:
                case_verdict = case.get("verdict", "Unknown")
                case_cfg = _VERDICT_CONFIG.get(case_verdict, _VERDICT_CONFIG["Suspicious"])
                similarity_pct = int(case.get("similarity", 0) * 100)

                st.markdown(f"""
                <div style="
                    border-left: 3px solid {case_cfg["border"]};
                    padding: 8px 12px; margin: 8px 0;
                    background: {case_cfg["bg"]}; border-radius: 4px;
                ">
                    <div style="font-size: 0.8rem; color: {case_cfg["color"]}; font-weight: 600;">
                        {case_cfg["emoji"]} {case_verdict} &nbsp;·&nbsp;
                        {case.get("type", "").replace("_", " ").title()} &nbsp;·&nbsp;
                        {similarity_pct}% similar
                    </div>
                    <div style="font-size: 0.85rem; color: #555; margin-top: 4px;">
                        {case.get("text", "")[:120]}{"..." if len(case.get("text","")) > 120 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
