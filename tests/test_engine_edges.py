import random

import pytest

from mercor_engine.engine import AdaptiveAssessmentEngine, AssessmentConfig
from mercor_engine.models import Difficulty, Question


def question(identifier, difficulty, answer="A"):
    return Question(identifier, f"Q{identifier}", ["A", "B"], answer, difficulty, "Python")


def test_engine_requires_questions():
    with pytest.raises(ValueError, match="At least one question"):
        AdaptiveAssessmentEngine([])


def test_config_rejects_invalid_values():
    with pytest.raises(ValueError):
        AssessmentConfig(question_count=0)
    with pytest.raises(ValueError):
        AssessmentConfig(promote_after=0)
    with pytest.raises(ValueError):
        AssessmentConfig(demote_after=0)


@pytest.mark.parametrize(
    ("score", "expected"),
    [(100, "MERCOR ELITE"), (95, "MERCOR ELITE"), (94, "HIGH PERFORMER"), (80, "HIGH PERFORMER"), (79, "STRONG"), (60, "STRONG"), (59, "DEVELOPING"), (40, "DEVELOPING"), (39, "NEEDS IMPROVEMENT")],
)
def test_rating_boundaries(score, expected):
    assert AdaptiveAssessmentEngine.rating(score) == expected


def test_falls_back_when_current_difficulty_has_no_unused_question():
    questions = [question(1, Difficulty.BEGINNER), question(2, Difficulty.INTERMEDIATE)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(1))
    result = engine.run("Ada", lambda q, _: q.answer, AssessmentConfig(question_count=2, starting_difficulty=Difficulty.ELITE, promote_after=5))
    assert result.total_questions == 2
    assert result.correct_answers == 2


def test_never_repeats_questions():
    questions = [question(i, Difficulty.BEGINNER) for i in range(1, 5)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(4))
    result = engine.run("Ada", lambda q, _: q.answer, AssessmentConfig(question_count=4, starting_difficulty=Difficulty.BEGINNER, promote_after=10))
    ids = [answer.question_id for answer in result.answers]
    assert len(ids) == len(set(ids)) == 4


def test_engine_stops_when_question_pool_is_exhausted():
    engine = AdaptiveAssessmentEngine([question(1, Difficulty.BEGINNER)], random.Random(1))
    result = engine.run("Ada", lambda q, _: q.answer, AssessmentConfig(question_count=10, starting_difficulty=Difficulty.BEGINNER))
    assert result.total_questions == 1


def test_promotion_is_capped_at_elite():
    questions = [question(i, Difficulty.ELITE) for i in range(1, 4)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(1))
    result = engine.run("Ada", lambda q, _: q.answer, AssessmentConfig(question_count=3, starting_difficulty=Difficulty.ELITE, promote_after=1))
    assert result.ending_difficulty == "Elite"


def test_demotion_is_capped_at_beginner():
    questions = [question(i, Difficulty.BEGINNER) for i in range(1, 4)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(1))
    result = engine.run("Ada", lambda q, _: "B", AssessmentConfig(question_count=3, starting_difficulty=Difficulty.BEGINNER, demote_after=1))
    assert result.ending_difficulty == "Beginner"


def test_blank_candidate_name_becomes_anonymous():
    engine = AdaptiveAssessmentEngine([question(1, Difficulty.BEGINNER)], random.Random(1))
    result = engine.run("   ", lambda q, _: q.answer, AssessmentConfig(question_count=1))
    assert result.name == "Anonymous"
