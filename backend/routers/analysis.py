from fastapi import APIRouter, Depends, HTTPException, Request, status
from backend.models.schemas import AnalysisRequest, AnalysisResponse
from backend.services.analysis_service import AnalysisService, get_analysis_service
from backend.services.rate_limiter import RateLimiter, get_rate_limiter

router = APIRouter(prefix="/api/v1", tags=["analysis"])


def _get_client_ip(request: Request) -> str:
    """Extract real client IP. Behind ngrok/reverse-proxy uses X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/analyze", response_model=AnalysisResponse,
             summary="Check content for scam signs")
async def analyze(
    request: Request,
    body: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> AnalysisResponse:
    # Check IP rate limit
    client_ip = _get_client_ip(request)
    rate_status = limiter.check_and_increment(client_ip)

    if not rate_status["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Daily limit reached",
                "message": (
                    f"Free plan: {rate_status['limit']} checks/day. "
                    "Resets at midnight UTC."
                ),
                "limit": rate_status["limit"],
                "count": rate_status["count"],
                "reset_at": rate_status["reset_at"],
            },
        )

    try:
        return service.analyze(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis error. Try again later.",
        ) from exc


@router.get("/rate-limit", summary="Check your current rate limit status")
async def rate_limit_status(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> dict:
    """Lets the frontend show how many checks remain today."""
    client_ip = _get_client_ip(request)
    return limiter.get_status(client_ip)
