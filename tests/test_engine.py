import random

from mercor_engine.engine import AdaptiveAssessmentEngine, AssessmentConfig
from mercor_engine.models import Difficulty, Question


def question(identifier, difficulty, answer="A"):
    return Question(identifier, f"Q{identifier}", ["A", "B"], answer, difficulty, "Python")


def test_promotes_after_correct_streak():
    questions = [question(i, Difficulty.BEGINNER) for i in range(1, 3)] + [question(i, Difficulty.INTERMEDIATE) for i in range(3, 6)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(1))
    result = engine.run("Ada", lambda q, _: q.answer, AssessmentConfig(question_count=3, starting_difficulty=Difficulty.BEGINNER, promote_after=2))
    assert result.score == 100.0
    assert result.ending_difficulty == "Intermediate"


def test_demotes_after_incorrect_streak():
    questions = [question(i, Difficulty.INTERMEDIATE) for i in range(1, 3)] + [question(i, Difficulty.BEGINNER) for i in range(3, 6)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(1))
    result = engine.run("Ada", lambda q, _: "B", AssessmentConfig(question_count=3, starting_difficulty=Difficulty.INTERMEDIATE, demote_after=2))
    assert result.score == 0.0
    assert result.ending_difficulty == "Beginner"


def test_category_accuracy():
    questions = [question(1, Difficulty.BEGINNER), question(2, Difficulty.BEGINNER)]
    engine = AdaptiveAssessmentEngine(questions, random.Random(1))
    result = engine.run("Ada", lambda q, i: q.answer if i == 0 else "B", AssessmentConfig(question_count=2, starting_difficulty=Difficulty.BEGINNER, promote_after=5))
    assert result.category_accuracy["Python"] == 50.0
