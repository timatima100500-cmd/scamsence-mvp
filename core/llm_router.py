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
    Mock router — ScamAnalyzer pattern detection + Knowledge Base enrichment.
    День 8 заменит на Ollama/Claude.
    """
    MODEL_NAME = "mock-analyzer-v2"

    def __init__(self):
        self._analyzer = ScamAnalyzer()
        self._kb = None  # KB инициализируется лениво

    def _get_kb(self):
        """Ленивый импорт KB — избегаем circular imports и замедления старта."""
        if self._kb is None:
            try:
                from knowledge_base.chroma_client import get_knowledge_base
                self._kb = get_knowledge_base()
            except Exception:
                self._kb = None
        return self._kb

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        start = time.monotonic()

        result = self._analyzer.analyze(
            content=request.content,
            content_type=request.content_type.value,
            language=request.language,
        )

        red_flags = [
            RedFlag(
                pattern=m.pattern_type.value,
                description=m.description,
                severity=m.severity,
            )
            for m in result.matches
        ]

        verdict, explanation, recommendations = self._build_verdict(result.normalized_score, result)

        # Обогащаем похожими кейсами из KB (опционально)
        similar_cases = self._fetch_similar_cases(request.content)

        # Если KB нашла уверенные скамы, но паттерны не сработали — добавляем сигнал
        if similar_cases:
            scam_matches = [c for c in similar_cases if c["verdict"] == "Scam" and c["similarity"] > 0.6]
            if scam_matches and result.normalized_score < 70:
                top = scam_matches[0]
                explanation += (
                    f" Similar known scam detected (type: {top['type']}, "
                    f"similarity: {top['similarity']:.0%})."
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
            similar_cases=similar_cases,
        )

    def _fetch_similar_cases(self, text: str) -> list[dict]:
        """Запрашивает похожие кейсы из KB. Пустой список если KB недоступна."""
        kb = self._get_kb()
        if kb is None:
            return []
        return kb.similarity_search(text, n_results=3, min_similarity=0.4)

    @staticmethod
    def _build_verdict(score: int, result: AnalysisResult) -> tuple:
        detected = {m.pattern_type for m in result.matches}

        if score >= 70:
            recs = [
                "Do not click any links in this message.",
                "Do not share personal data or send money.",
                "Block and report the sender.",
            ]
            if PatternType.payment_red_flag in detected:
                recs.append("If you already sent money, contact your bank immediately.")
            if PatternType.data_harvesting in detected:
                recs.append("If you shared credentials, change your passwords now.")
            return (
                Verdict.scam,
                f"High fraud probability. Detected {len(result.matches)} red flag(s) "
                f"across {len(detected)} pattern category(ies).",
                recs,
            )

        elif score >= 45:
            return (
                Verdict.likely_scam,
                "Multiple suspicious signals found. Verify the sender before taking any action.",
                [
                    "Check the sender via the official website or phone number.",
                    "Do not act under time pressure — scammers create false urgency.",
                    "Call the organization directly using a number from their official site.",
                ],
            )

        elif score >= 20:
            return (
                Verdict.suspicious,
                "Some suspicious elements detected. Proceed with caution.",
                [
                    "Verify the sender through a different channel.",
                    "Do not click unfamiliar links.",
                ],
            )

        else:
            return (
                Verdict.legitimate,
                "No significant fraud indicators found. Message appears legitimate.",
                ["Stay vigilant — even trusted channels can be compromised."],
            )


def get_router() -> BaseLLMRouter:
    return MockLLMRouter()
