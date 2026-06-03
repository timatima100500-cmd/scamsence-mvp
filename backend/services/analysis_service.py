from loguru import logger
from backend.models.schemas import AnalysisRequest, AnalysisResponse
from core.llm_router import BaseLLMRouter, get_router


class AnalysisService:
    def __init__(self, router: BaseLLMRouter | None = None) -> None:
        self._router = router or get_router()

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        logger.info("Analyzing | type={} | len={}", request.content_type.value, len(request.content))
        response = self._router.analyze(request)
        logger.info("Result | verdict={} | prob={}% | time={}ms",
                    response.verdict.value, response.probability, response.analysis_time_ms)
        return response


_instance: AnalysisService | None = None

def get_analysis_service() -> AnalysisService:
    global _instance
    if _instance is None:
        _instance = AnalysisService()
    return _instance
