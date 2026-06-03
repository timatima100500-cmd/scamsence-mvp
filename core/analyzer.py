"""
core/analyzer.py — ScamAnalyzer: движок распознавания паттернов

Использует regex + весовое scoring вместо простого keyword matching.
Это позволяет точнее определять границы слов и комбинации паттернов.

День 8: результат analyzer будет передаваться в LLM как context,
чтобы LLM фокусировалась на сложных случаях, а не пересчитывала очевидное.
"""

import re
from core.models import AnalysisContext, AnalysisResult, PatternMatch, PatternType


# ── Паттерны с весами ────────────────────────────────────────────────────────
# Каждый паттерн: (regex, description, severity, score_contribution)
# score_contribution суммируется — комбо нескольких паттернов = высокий score

_URGENCY_PATTERNS: list[tuple] = [
    (r"\b(act now|act immediately)\b",          "Calls for immediate action",               8, 30.0),
    (r"\b(urgent|urgently)\b",                  "Urgency keyword",                          7, 25.0),
    (r"\b(limited time|expires? (today|soon))\b","Limited-time pressure",                   8, 28.0),
    (r"\b(last chance|final (notice|warning))\b","Final warning language",                  8, 30.0),
    (r"\baccount.{0,20}(closed|suspended|blocked|terminated)\b", "Account suspension threat",9, 35.0),
    (r"\bverify.{0,20}(within|in) \d+ (hours?|minutes?|days?)\b","Verification deadline",   8, 30.0),
    # Russian urgency
    (r"\bнемедленно\b",                          "Urgency (RU): немедленно",                8, 25.0),
    (r"\bсрочно\b",                              "Urgency (RU): срочно",                    7, 22.0),
    (r"\bограниченное время\b",                  "Urgency (RU): ограниченное время",        8, 28.0),
    (r"\bваш аккаунт.{0,30}(заблокирован|закрыт|приостановлен)\b","Account threat (RU)",    9, 35.0),
]

_IMPERSONATION_PATTERNS: list[tuple] = [
    (r"\b(sberbank|tinkoff|vtb|alfabank|alfa-bank)\b", "Russian bank impersonation",       9, 35.0),
    (r"\b(apple|microsoft|google|amazon|netflix|paypal)\bsupport",
                                                 "Tech company support impersonation",      9, 35.0),
    (r"\b(irs|fbi|cia|dhs|interpol|europol)\b",  "Government agency impersonation",        10, 40.0),
    (r"\b(налоговая|фнс|мвд|фсб|госуслуги)\b",   "Russian government impersonation",      10, 40.0),
    (r"\bofficial.{0,10}(notice|communication|message)\b", "Fake official communication",  8, 28.0),
    (r"\byour (bank|financial institution)\b",    "Generic bank impersonation",             7, 25.0),
    (r"\btechnical support\b",                    "Tech support scam language",             8, 28.0),
]

_TOO_GOOD_PATTERNS: list[tuple] = [
    (r"\b(you('ve| have) won|congratulations.{0,30}(won|selected|chosen))\b",
                                                 "Prize/lottery win claim",                 9, 38.0),
    (r"\b(guaranteed|100%.{0,10}(return|profit|yield))\b","Guaranteed returns claim",       9, 35.0),
    (r"\b\d{3,}%.{0,10}(return|profit|gain|roi)\b", "Unrealistic % return",               10, 40.0),
    (r"\b(free (iphone|macbook|gift card|vacation|cruise))\b","Free luxury item bait",      8, 30.0),
    (r"\bunclaimed.{0,20}(funds?|money|prize|inheritance)\b","Unclaimed funds scam",        9, 38.0),
    (r"\byou('ve| have) been selected\b",         "Fake selection language",               7, 25.0),
    (r"\bвы выиграли\b",                          "Prize claim (RU)",                      9, 38.0),
    (r"\bгарантированный доход\b",                "Guaranteed income (RU)",                9, 35.0),
    (r"\bбесплатно\b",                            "Free offer (RU)",                        6, 18.0),
]

_PAYMENT_PATTERNS: list[tuple] = [
    (r"\b(bitcoin|btc|ethereum|eth|usdt|crypto(currency)?)\b","Crypto payment request",   9, 35.0),
    (r"\b(gift card|itunes card|google play card|amazon card)\b","Gift card payment",      10, 40.0),
    (r"\bwire transfer\b",                        "Wire transfer request",                 8, 30.0),
    (r"\b(western union|moneygram|money gram)\b", "Informal wire service",                 9, 38.0),
    (r"\bsend (money|funds|payment).{0,30}(immediately|now|today)\b","Urgent money send", 10, 42.0),
    (r"\bdo not (tell|inform|contact).{0,30}(bank|anyone)\b","Secrecy instruction",       10, 45.0),
    (r"\bбиткоин\b",                              "Crypto request (RU)",                   9, 35.0),
    (r"\bподарочн.{1,5} карт\b",                  "Gift card (RU)",                       10, 40.0),
]

_DATA_HARVESTING_PATTERNS: list[tuple] = [
    (r"\b(social security|ssn|sin number)\b",     "SSN request",                          10, 45.0),
    (r"\b(password|passphrase|pin).{0,20}(enter|provide|confirm|send)\b","Password request",10,45.0),
    (r"\b(bank account|routing number|account number).{0,20}(provide|send|enter)\b",
                                                  "Bank account request",                 10, 45.0),
    (r"\bverif(y|ication).{0,20}(identity|personal|information)\b","Identity verification",7, 22.0),
    (r"\bupdate.{0,20}(payment|billing|card) (info|information|details)\b",
                                                  "Payment info update",                   8, 30.0),
    (r"\bпароль\b",                               "Password request (RU)",                10, 45.0),
    (r"\bномер карты\b",                          "Card number request (RU)",              10, 45.0),
]

_SUSPICIOUS_LINK_PATTERNS: list[tuple] = [
    (r"\b(bit\.ly|tinyurl|t\.co|goo\.gl|ow\.ly|short\.link)\b", "URL shortener",          7, 22.0),
    (r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",            "IP address URL",         9, 35.0),
    (r"\b\w+(paypa1|g00gle|amaz0n|microsft|app1e)\.\w+",         "Typosquatting domain",  10, 40.0),
    (r"\b(verify|secure|login|account|update)\.\w{3,}\.\w{2,3}", "Phishing-style domain",  8, 28.0),
]

# Все группы паттернов с их типом
_ALL_PATTERN_GROUPS: list[tuple] = [
    (PatternType.urgency,            _URGENCY_PATTERNS),
    (PatternType.impersonation,      _IMPERSONATION_PATTERNS),
    (PatternType.too_good_to_be_true,_TOO_GOOD_PATTERNS),
    (PatternType.payment_red_flag,   _PAYMENT_PATTERNS),
    (PatternType.data_harvesting,    _DATA_HARVESTING_PATTERNS),
    (PatternType.suspicious_link,    _SUSPICIOUS_LINK_PATTERNS),
]

# Бонусный score за комбинации — потому что реальные скамы используют несколько паттернов
_COMBO_BONUS: dict[frozenset, float] = {
    frozenset({PatternType.urgency, PatternType.impersonation}): 15.0,
    frozenset({PatternType.urgency, PatternType.payment_red_flag}): 20.0,
    frozenset({PatternType.too_good_to_be_true, PatternType.payment_red_flag}): 20.0,
    frozenset({PatternType.impersonation, PatternType.data_harvesting}): 25.0,
}


class ScamAnalyzer:
    """
    Главный движок распознавания скамов.
    Использует regex с word boundaries — точнее чем простой substring search.
    Комбо-бонусы отражают реальность: скамы всегда используют несколько крючков одновременно.
    """

    def analyze(self, content: str, content_type: str, language: str = "auto") -> AnalysisResult:
        """Полный анализ контента — возвращает AnalysisResult с матчами и score."""
        ctx = AnalysisContext(content=content, content_type=content_type, language=language)
        result = AnalysisResult(context=ctx)
        text = content.lower()

        # Прогоняем все группы паттернов
        detected_types: set[PatternType] = set()
        for pattern_type, patterns in _ALL_PATTERN_GROUPS:
            matches = self._match_group(text, pattern_type, patterns)
            for m in matches:
                result.add_match(m)
                detected_types.add(pattern_type)

        # Начисляем комбо-бонусы за сочетания паттернов
        self._apply_combo_bonuses(result, detected_types)

        return result

    def _match_group(self, text: str, pattern_type: PatternType,
                     patterns: list[tuple]) -> list[PatternMatch]:
        """Проверяет одну группу паттернов, возвращает все совпавшие."""
        found: list[PatternMatch] = []
        seen_descriptions: set[str] = set()

        for regex, description, severity, score_contribution in patterns:
            match = re.search(regex, text, re.IGNORECASE)
            if match and description not in seen_descriptions:
                found.append(PatternMatch(
                    pattern_type=pattern_type,
                    matched_text=match.group(0),
                    description=description,
                    severity=severity,
                    score_contribution=score_contribution,
                ))
                seen_descriptions.add(description)

        return found

    def _apply_combo_bonuses(self, result: AnalysisResult,
                              detected_types: set[PatternType]) -> None:
        """Комбинация нескольких паттернов — сильный сигнал что это скам."""
        for combo, bonus in _COMBO_BONUS.items():
            if combo.issubset(detected_types):
                result.raw_score += bonus
                result.normalized_score = min(int(result.raw_score), 100)
