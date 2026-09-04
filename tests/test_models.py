import pytest

from mercor_engine.models import Difficulty, Question


def payload(**overrides):
    value = {
        "id": 1,
        "question": "What?",
        "options": ["A", "B"],
        "answer": "A",
        "difficulty": "Beginner",
    }
    value.update(overrides)
    return value


def test_difficulty_from_value_accepts_enum_int_and_name():
    assert Difficulty.from_value(Difficulty.ELITE) is Difficulty.ELITE
    assert Difficulty.from_value(4) is Difficulty.ELITE
    assert Difficulty.from_value("elite") is Difficulty.ELITE
    assert Difficulty.INTERMEDIATE.label == "Intermediate"


@pytest.mark.parametrize("missing", ["id", "question", "options", "answer", "difficulty"])
def test_question_rejects_missing_required_field(missing):
    value = payload()
    del value[missing]
    with pytest.raises(ValueError, match="missing fields"):
        Question.from_dict(value)


def test_question_requires_at_least_two_options():
    with pytest.raises(ValueError, match="at least two options"):
        Question.from_dict(payload(options=["A"]))


def test_question_answer_must_be_an_option():
    with pytest.raises(ValueError, match="answer must exist"):
        Question.from_dict(payload(answer="C"))


def test_question_from_dict_applies_optional_defaults():
    question = Question.from_dict(payload())
    assert question.category == "General"
    assert question.explanation == ""
