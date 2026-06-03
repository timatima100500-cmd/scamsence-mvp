"""
frontend/pages/url_check.py - URL Check page

Static structural analysis (no HTTP requests to suspicious sites) +
full AI analysis via POST /api/v1/analyze (content_type=url).
"""
import re
import streamlit as st
import requests
import json
from urllib.parse import urlparse

from frontend.components.result_card import render_result_card

API_URL = "http://127.0.0.1:8000/api/v1/analyze"

_URL_EXAMPLES = [
    "http://sberbank-secure-login.xyz/verify?token=abc123",
    "https://apple-support-helpdesk.info/fix-your-account",
    "http://bit.ly/free-iphone-winner-2026",
    "https://paypa1.com/login/security-check",
    "http://microsoft-tech-support-team.xyz/call-now",
    "https://invest-crypto-guaranteed-500percent.io/join",
]

_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "buff.ly", "is.gd", "rebrand.ly", "short.link", "cutt.ly",
}

_BRAND_PATTERNS = [
    ("paypal",    ["paypa1", "paypall", "paypal-secure", "paypal-login"]),
    ("google",    ["g00gle", "googlle", "google-secure"]),
    ("apple",     ["app1e", "apple-support", "apple-helpdesk", "apple-promo"]),
    ("microsoft", ["micros0ft", "microsoft-helpdesk", "microsoft-support-team"]),
    ("amazon",    ["amaz0n", "amazon-secure", "amazon-promo"]),
    ("sberbank",  ["sberbank-alert", "sberbank-secure", "sberbank-login"]),
    ("facebook",  ["faceb00k", "facebook-login", "facebook-security"]),
]

_SUSPICIOUS_TLDS = {".xyz", ".info", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".icu"}

_SUSPICIOUS_KEYWORDS = [
    "secure", "login", "verify", "confirm", "update", "account",
    "helpdesk", "support-team", "alert", "blocked", "suspended",
    "winner", "prize", "free", "guaranteed", "claim",
]


def _analyze_url(url: str) -> dict:
    """
    Статический анализ структуры URL без сетевых запросов.
    Не делаем запросы к подозрительным сайтам — это и безопасно, и быстро.
    """
    url_to_parse = url if url.startswith(("http://", "https://")) else "https://" + url
    parsed = urlparse(url_to_parse)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    red_flags = []

    # HTTP без шифрования на чувствительных страницах
    if url.startswith("http://") and any(kw in url.lower() for kw in ["login", "verify", "account", "bank", "pay"]):
        red_flags.append({"flag": "🔓 HTTP без шифрования", "severity": "high",
                          "detail": "Чувствительные данные передаются без SSL"})

    # URL shortener скрывает реальный домен
    if any(short in domain for short in _SHORTENERS):
        red_flags.append({"flag": "🔗 URL shortener", "severity": "high",
                          "detail": f"{domain} скрывает реальный адрес назначения"})

    # Подозрительный TLD
    for tld in _SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            red_flags.append({"flag": f"🌐 Подозрительный TLD {tld}", "severity": "medium",
                              "detail": "Мошенники часто используют дешёвые TLD"})
            break

    # Typosquatting — имитация брендов
    for brand, fakes in _BRAND_PATTERNS:
        if brand not in domain:
            for fake in fakes:
                if fake in domain:
                    red_flags.append({"flag": f"🎭 Typosquatting: {brand}", "severity": "critical",
                                      "detail": f"Домен имитирует {brand}.com — классический фишинг"})
                    break

    # Бренд в домене, но не официальный сайт
    for brand, _ in _BRAND_PATTERNS:
        official = f"{brand}.com"
        if (brand in domain and official not in domain
                and not domain.endswith(f".{brand}.com")
                and not any(f["flag"].startswith("🎭") and brand in f["flag"] for f in red_flags)):
            red_flags.append({"flag": f"⚠️ {brand.capitalize()} в домене", "severity": "medium",
                              "detail": f"Содержит '{brand}', но это не {brand}.com"})

    # Много фишинговых ключевых слов
    found_kw = [kw for kw in _SUSPICIOUS_KEYWORDS if kw in path or kw in domain]
    if len(found_kw) >= 2:
        red_flags.append({"flag": "🔑 Фишинговые ключевые слова", "severity": "medium",
                          "detail": f"Найдено: {', '.join(found_kw[:4])}"})

    # Много дефисов в домене
    if domain.count("-") >= 3:
        red_flags.append({"flag": "➖ Много дефисов", "severity": "low",
                          "detail": f"{domain.count('-')} дефиса — нетипично для легитимных сайтов"})

    # IP вместо домена
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}", domain):
        red_flags.append({"flag": "🔢 IP вместо домена", "severity": "high",
                          "detail": "Легитимные сервисы используют доменные имена"})

    return {
        "scheme": parsed.scheme,
        "domain": domain,
        "path": parsed.path,
        "has_params": bool(parsed.query),
        "red_flags": red_flags,
    }


def _severity_icon(severity: str) -> str:
    return {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(severity, "⚪")


def _call_api(content: str) -> dict | None:
    """Отправляет URL в API для AI-анализа."""
    try:
        resp = requests.post(API_URL, json={"content": content, "content_type": "url"}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API недоступен. Запусти: `uvicorn backend.app:app --reload`")
    except requests.exceptions.Timeout:
        st.error("⏱️ API не ответил за 30 секунд.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP {e}")
    except json.JSONDecodeError:
        st.error("❌ Некорректный ответ от API.")
    return None


def render() -> None:
    """Renders the URL Check page."""
    st.markdown("## 🔗 URL Check")
    st.markdown(
        "Введи подозрительную ссылку — разберём структуру домена, "
        "найдём typosquatting, URL shorteners и другие красные флаги."
    )
    st.markdown("---")

    col_input, col_ex = st.columns([2.5, 1])
    with col_input:
        url_input = st.text_input(
            "🔗 URL для проверки",
            placeholder="https://sberbank-secure-login.xyz/verify",
            key="url_input_field",
        )
    with col_ex:
        st.markdown("<br>", unsafe_allow_html=True)
        example_url = st.selectbox(
            "Примеры",
            options=["— пример —"] + _URL_EXAMPLES,
            key="url_example_select",
            label_visibility="collapsed",
        )

    # Подставляем пример если поле пустое
    active_url = url_input.strip() or (example_url if example_url != "— пример —" else "")

    col_l, col_c, col_r = st.columns([2, 1.5, 2])
    with col_c:
        analyze = st.button("🔍 Проверить URL", type="primary",
                            use_container_width=True, key="analyze_url_btn")

    # Статический анализ — показываем сразу как только есть URL
    if active_url:
        st.markdown("---")
        st.markdown("#### 🔬 Разбор структуры URL")
        info = _analyze_url(active_url)

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            scheme = info["scheme"].upper() or "HTTP"
            icon = "🟢" if scheme == "HTTPS" else "🔴"
            st.metric("Протокол", f"{icon} {scheme}")
        with col_p2:
            st.metric("Домен", info["domain"] or "—")
        with col_p3:
            path_short = info["path"][:28] + "…" if len(info["path"]) > 28 else info["path"]
            st.metric("Путь", path_short or "/")
        with col_p4:
            st.metric("Параметры", "Есть" if info["has_params"] else "Нет")

        static_flags = info["red_flags"]
        if static_flags:
            st.markdown("**Найдено при структурном анализе:**")
            for item in static_flags:
                st.markdown(f"{_severity_icon(item['severity'])} **{item['flag']}** — {item['detail']}")
        else:
            st.success("✅ Структура URL не вызывает подозрений — но это не гарантия!")

    # AI-анализ через API
    if analyze:
        if not active_url:
            st.warning("⚠️ Введи URL для проверки.")
        else:
            with st.spinner("Анализируем URL через AI..."):
                result = _call_api(active_url)
            if result:
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.insert(0, {
                    "text": f"[URL] {active_url[:60]}",
                    "verdict": result.get("verdict", "Unknown"),
                    "probability": result.get("scam_probability", 0),
                    "content_type": "url",
                })
                st.markdown("---")
                render_result_card(result)
                verdict = result.get("verdict", "")
                if verdict in ("Scam", "Likely Scam"):
                    st.error(
                        "🔗 **URL-совет:** Не переходи по этой ссылке. "
                        "Сообщи о фишинге: https://safebrowsing.google.com/safebrowsing/report_phish/"
                    )
                elif verdict == "Suspicious":
                    st.warning(
                        "🔗 **URL-совет:** Проверь через VirusTotal.com или "
                        "Google Transparency Report перед переходом."
                    )
