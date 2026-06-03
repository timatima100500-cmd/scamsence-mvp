from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    text = "text"
    email = "email"
    url = "url"
    sms = "sms"  # SMS/messengers — sent by Analyzer page frontend


class Verdict(str, Enum):
    scam = "Scam"
    likely_scam = "Likely Scam"
    suspicious = "Suspicious"
    legitimate = "Legitimate"


class AnalysisRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=50000)
    content_type: ContentType = ContentType.text
    language: str = "auto"

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "Congratulations! You won $1,000,000. Send your SSN to claim.",
                "content_type": "text",
                "language": "auto",
            }
        }
    }


class RedFlag(BaseModel):
    pattern: str
    description: str
    severity: int = Field(..., ge=1, le=10)


class AnalysisResponse(BaseModel):
    verdict: Verdict
    probability: int = Field(..., ge=0, le=100)
    red_flags: list[RedFlag] = []
    explanation: str
    recommendations: list[str] = []
    model_used: str
    analysis_time_ms: int
    similar_cases: list[dict[str, Any]] = []

    def format_text(self) -> str:
        flags = "\n".join(f"  - {f.description}" for f in self.red_flags)
        recs = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(self.recommendations))
        return (
            f"Verdict: {self.verdict.value} - {self.probability}%\n\n"
            f"Red flags:\n{flags}\n\nExplanation:\n{self.explanation}\n\n"
            f"Recommendations:\n{recs}"
        )
