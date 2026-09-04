from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from time import monotonic

from .models import AssessmentResult, Difficulty, Question, QuestionResult


@dataclass(frozen=True)
class AssessmentConfig:
    question_count: int = 10
    starting_difficulty: Difficulty = Difficulty.INTERMEDIATE
    promote_after: int = 2
    demote_after: int = 2

    def __post_init__(self) -> None:
        if self.question_count < 1:
            raise ValueError("question_count must be positive")
        if self.promote_after < 1 or self.demote_after < 1:
            raise ValueError("adaptation thresholds must be positive")


class AdaptiveAssessmentEngine:
    def __init__(self, questions: Sequence[Question], rng: random.Random | None = None):
        if not questions:
            raise ValueError("At least one question is required")
        self.questions = list(questions)
        self.rng = rng or random.Random()

    @staticmethod
    def rating(score: float) -> str:
        if score >= 95:
            return "MERCOR ELITE"
        if score >= 80:
            return "HIGH PERFORMER"
        if score >= 60:
            return "STRONG"
        if score >= 40:
            return "DEVELOPING"
        return "NEEDS IMPROVEMENT"

    def _pick_question(self, difficulty: Difficulty, used_ids: set[int]) -> Question | None:
        candidates = [q for q in self.questions if q.difficulty == difficulty and q.id not in used_ids]
        if not candidates:
            candidates = [q for q in self.questions if q.id not in used_ids]
        return self.rng.choice(candidates) if candidates else None

    def run(self, name: str, answer_provider: Callable[[Question, int], str], config: AssessmentConfig | None = None) -> AssessmentResult:
        config = config or AssessmentConfig()
        current = config.starting_difficulty
        starting = current
        used_ids: set[int] = set()
        streak = 0
        answers: list[QuestionResult] = []
        path: list[str] = []
        started = monotonic()

        for index in range(config.question_count):
            question = self._pick_question(current, used_ids)
            if question is None:
                break
            used_ids.add(question.id)
            path.append(current.label)
            selected = answer_provider(question, index)
            correct = selected == question.answer
            answers.append(QuestionResult(question.id, question.category, current.label, correct, selected, question.answer))

            if correct:
                streak = streak + 1 if streak >= 0 else 1
                if streak >= config.promote_after:
                    current = Difficulty(min(int(Difficulty.ELITE), int(current) + 1))
                    streak = 0
            else:
                streak = streak - 1 if streak <= 0 else -1
                if abs(streak) >= config.demote_after:
                    current = Difficulty(max(int(Difficulty.BEGINNER), int(current) - 1))
                    streak = 0

        duration = round(monotonic() - started, 2)
        correct_count = sum(answer.correct for answer in answers)
        total = len(answers)
        score = round((correct_count / total) * 100, 2) if total else 0.0

        grouped: dict[str, list[bool]] = defaultdict(list)
        for answer in answers:
            grouped[answer.category].append(answer.correct)
        category_accuracy = {category: round(sum(values) / len(values) * 100, 2) for category, values in grouped.items()}

        return AssessmentResult(
            name=name.strip() or "Anonymous",
            score=score,
            correct_answers=correct_count,
            total_questions=total,
            duration_seconds=duration,
            rating=self.rating(score),
            timestamp=datetime.now(timezone.utc).isoformat(),
            starting_difficulty=starting.label,
            ending_difficulty=current.label,
            difficulty_path=path,
            category_accuracy=category_accuracy,
            answers=answers,
        )
