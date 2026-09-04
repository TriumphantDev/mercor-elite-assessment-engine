from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any


class Difficulty(IntEnum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    ELITE = 4

    @classmethod
    def from_value(cls, value: str | int | "Difficulty") -> "Difficulty":
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        normalized = str(value).strip().upper().replace(" ", "_")
        return cls[normalized]

    @property
    def label(self) -> str:
        return self.name.title()


@dataclass(frozen=True)
class Question:
    id: int
    question: str
    options: list[str]
    answer: str
    difficulty: Difficulty
    category: str = "General"
    explanation: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Question":
        required = {"id", "question", "options", "answer", "difficulty"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"Question missing fields: {', '.join(sorted(missing))}")
        options = payload["options"]
        if not isinstance(options, list) or len(options) < 2:
            raise ValueError(f"Question {payload['id']} needs at least two options")
        if payload["answer"] not in options:
            raise ValueError(f"Question {payload['id']} answer must exist in options")
        return cls(
            id=int(payload["id"]),
            question=str(payload["question"]).strip(),
            options=[str(option) for option in options],
            answer=str(payload["answer"]),
            difficulty=Difficulty.from_value(payload["difficulty"]),
            category=str(payload.get("category", "General")),
            explanation=str(payload.get("explanation", "")),
        )


@dataclass
class QuestionResult:
    question_id: int
    category: str
    difficulty: str
    correct: bool
    selected: str
    answer: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssessmentResult:
    name: str
    score: float
    correct_answers: int
    total_questions: int
    duration_seconds: float
    rating: str
    timestamp: str
    starting_difficulty: str
    ending_difficulty: str
    difficulty_path: list[str] = field(default_factory=list)
    category_accuracy: dict[str, float] = field(default_factory=dict)
    answers: list[QuestionResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["answers"] = [answer.to_dict() for answer in self.answers]
        return data
