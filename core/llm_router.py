import time
from abc import ABC, abstractmethod

from backend.models.schemas import AnalysisRequest, AnalysisResponse, RedFlag, Verdict
from core.analyzer import ScamAnalyzer
from core.models import AnalysisResult, PatternType


class BaseLLMRouter(ABC):
    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse: ...


class MockLLMRouter(BaseLLMRouter):
    """
    Mock router — использует ScamAnalyzer для реального pattern detection,
    но не вызывает внешний LLM. День 8 заменит на Ollama/Claude.
    """
    MODEL_NAME = "mock-analyzer-v2"

    def __init__(self):
        # ScamAnalyzer переиспользуется между запросами — он stateless
        self._analyzer = ScamAnalyzer()

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        start = time.monotonic()

        # Запускаем полный анализ паттернов
        result = self._analyzer.analyze(
            content=request.content,
            content_type=request.content_type.value,
            language=request.language,
        )

        # Конвертируем внутренние PatternMatch -> API RedFlag
        red_flags = [
            RedFlag(
                pattern=m.pattern_type.value,
                description=m.description,
                severity=m.severity,
            )
            for m in result.matches
        ]

        verdict, explanation, recommendations = self._build_verdict(
            result.normalized_score, result
        )

        ms = int((time.monotonic() - start) * 1000)

        return AnalysisResponse(
            verdict=verdict,
            probability=result.normalized_score,
            red_flags=red_flags,
            explanation=explanation,
            recommendations=recommendations,
            model_used=self.MODEL_NAME,
            analysis_time_ms=ms,
        )

    @staticmethod
    def _build_verdict(score: int, result: AnalysisResult) -> tuple:
        detected = {m.pattern_type for m in result.matches}

        if score >= 70:
            recs = ["Do not click any links in this message.",
                    "Do not share personal data or send money.",
                    "Block and report the sender."]
            if PatternType.payment_red_flag in detected:
                recs.append("If you already sent money, contact your bank immediately.")
            if PatternType.data_harvesting in detected:
                recs.append("If you shared credentials, change your passwords now.")
            return (Verdict.scam,
                    f"High fraud probability. Detected {len(result.matches)} red flag(s) "
                    f"across {len(detected)} pattern category(ies).",
                    recs)

        elif score >= 45:
            return (Verdict.likely_scam,
                    "Multiple suspicious signals found. Verify the sender before taking any action.",
                    ["Check the sender via the official website or phone number.",
                     "Do not act under time pressure — scammers create false urgency.",
                     "Call the organization directly using a number from their official site."])

        elif score >= 20:
            return (Verdict.suspicious,
                    "Some suspicious elements detected. Proceed with caution.",
                    ["Verify the sender through a different channel.",
                     "Do not click unfamiliar links."])

        else:
            return (Verdict.legitimate,
                    "No significant fraud indicators found. Message appears legitimate.",
                    ["Stay vigilant — even trusted channels can be compromised."])


def get_router() -> BaseLLMRouter:
    return MockLLMRouter()
