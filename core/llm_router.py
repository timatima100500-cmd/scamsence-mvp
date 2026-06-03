import time
from abc import ABC, abstractmethod

from backend.models.schemas import AnalysisRequest, AnalysisResponse, RedFlag, Verdict

_URGENCY = ["immediately", "urgent", "act now", "limited time", "account will be closed",
            "nemedlenno", "srochno", "sejchas"]
_TOO_GOOD = ["won", "winner", "free", "guaranteed", "500%", "1000%",
             "vyigrali", "besplatno", "podarok", "priz"]
_IMPERSONATION = ["apple", "microsoft", "amazon", "google", "support team",
                  "bank", "sberbank", "nalogovaya", "policiya"]
_PAYMENT = ["bitcoin", "crypto", "gift card", "wire transfer", "western union",
            "bitkoin", "kriptovalyuta", "podarochnaya karta"]


class BaseLLMRouter(ABC):
    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse: ...


class MockLLMRouter(BaseLLMRouter):
    MODEL_NAME = "mock-keyword-v1"

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        start = time.monotonic()
        text = request.content.lower()
        flags: list[RedFlag] = []
        score = 0

        hits = [w for w in _URGENCY if w in text]
        if hits:
            flags.append(RedFlag(pattern="urgency", description=f"Urgency pressure: {', '.join(hits[:3])}", severity=8))
            score += 35

        hits = [w for w in _TOO_GOOD if w in text]
        if hits:
            flags.append(RedFlag(pattern="too_good_to_be_true", description=f"Unrealistic promises: {', '.join(hits[:3])}", severity=9))
            score += 40

        hits = [w for w in _IMPERSONATION if w in text]
        if hits:
            flags.append(RedFlag(pattern="impersonation", description=f"Impersonates org: {', '.join(hits[:3])}", severity=9))
            score += 35

        hits = [w for w in _PAYMENT if w in text]
        if hits:
            flags.append(RedFlag(pattern="payment_red_flag", description=f"Suspicious payment: {', '.join(hits[:3])}", severity=10))
            score += 30

        prob = min(score, 100)
        verdict, explanation, recommendations = self._verdict(prob)
        ms = int((time.monotonic() - start) * 1000)

        return AnalysisResponse(
            verdict=verdict, probability=prob, red_flags=flags,
            explanation=explanation, recommendations=recommendations,
            model_used=self.MODEL_NAME, analysis_time_ms=ms,
        )

    @staticmethod
    def _verdict(prob: int) -> tuple:
        if prob >= 70:
            return (Verdict.scam,
                    "High probability of fraud. Multiple classic scam signs detected.",
                    ["Do not click any links.", "Do not share personal data or money.",
                     "Block the sender and report it.", "If you sent money, contact your bank immediately."])
        elif prob >= 45:
            return (Verdict.likely_scam,
                    "Several signs point to fraud. Verify the source before acting.",
                    ["Check the sender via the official website.", "Do not rush - scammers create false urgency.",
                     "Call the official number to confirm."])
        elif prob >= 20:
            return (Verdict.suspicious,
                    "Some suspicious signs found. Confirm authenticity before acting.",
                    ["Contact the sender through a different channel.", "Do not click unfamiliar links."])
        else:
            return (Verdict.legitimate,
                    "No obvious fraud signs detected. Message appears legitimate.",
                    ["Stay vigilant - even legitimate channels can be compromised."])


def get_router() -> BaseLLMRouter:
    return MockLLMRouter()
