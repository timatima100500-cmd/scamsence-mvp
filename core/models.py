from dataclasses import dataclass, field
from enum import Enum


class PatternType(str, Enum):
    """Типы скам-паттернов — используются для классификации красных флагов."""
    urgency = "urgency"
    impersonation = "impersonation"
    too_good_to_be_true = "too_good_to_be_true"
    payment_red_flag = "payment_red_flag"
    data_harvesting = "data_harvesting"
    suspicious_link = "suspicious_link"
    romance_scam = "romance_scam"
    ai_voice_cloning = "ai_voice_cloning"


@dataclass
class PatternMatch:
    """Один найденный паттерн скама."""
    pattern_type: PatternType
    matched_text: str        # Что именно сработало в тексте
    description: str         # Человекочитаемое описание
    severity: int            # 1-10
    score_contribution: float  # Вклад в итоговый score


@dataclass
class AnalysisContext:
    """Контекст запроса — передаётся через весь pipeline."""
    content: str
    content_type: str
    language: str = "auto"
    char_count: int = 0
    word_count: int = 0

    def __post_init__(self):
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())


@dataclass
class AnalysisResult:
    """Внутренний результат ScamAnalyzer — до форматирования в API-ответ."""
    context: AnalysisContext
    matches: list[PatternMatch] = field(default_factory=list)
    raw_score: float = 0.0
    normalized_score: int = 0   # 0-100
    complexity: str = "low"     # low / medium / high — для LLM routing (День 8)

    def add_match(self, match: PatternMatch) -> None:
        """Добавляет паттерн и пересчитывает score."""
        self.matches.append(match)
        self.raw_score += match.score_contribution
        self.normalized_score = min(int(self.raw_score), 100)
        # Сложность определяет какую LLM использовать (День 8)
        if self.normalized_score >= 60 or len(self.matches) >= 3:
            self.complexity = "high"
        elif self.normalized_score >= 30:
            self.complexity = "medium"
