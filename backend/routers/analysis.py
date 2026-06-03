from fastapi import APIRouter, Depends, HTTPException, status
from backend.models.schemas import AnalysisRequest, AnalysisResponse
from backend.services.analysis_service import AnalysisService, get_analysis_service

router = APIRouter(prefix="/api/v1", tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse,
             summary="Check content for scam signs")
async def analyze(
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    try:
        return service.analyze(request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Analysis error. Try again later.") from exc
