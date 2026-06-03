from enum import Enum
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    text = "text"
    email = "email"
    url = "url"


class Verdict(str, Enum):
    scam = "Scam"
    likely_scam = "Likely Scam"
    suspicious = "Suspicious"
    legitimate = "Legitimate"


class AnalysisRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=10000)
    content_type: ContentType = ContentType.text
    language: str = "auto"

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "Pozdravlyaem! Vy vyigrali iPhone 15. Pereydte po ssylke nemedlenno!",
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

    def format_text(self) -> str:
        flags = "\n".join(f"  - {f.description}" for f in self.red_flags)
        recs = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(self.recommendations))
        return (
            f"Verdict: {self.verdict.value} - {self.probability}%\n\n"
            f"Red flags:\n{flags}\n\nExplanation:\n{self.explanation}\n\nRecommendations:\n{recs}"
        )
