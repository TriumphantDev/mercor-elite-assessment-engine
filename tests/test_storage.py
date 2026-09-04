import json

import pytest

from mercor_engine.models import Difficulty
from mercor_engine.storage import JSONStorage, QuestionRepository, ResultRepository, StorageError


def valid_question(identifier=1):
    return {
        "id": identifier,
        "question": "Pick A",
        "options": ["A", "B"],
        "answer": "A",
        "difficulty": "Beginner",
        "category": "Testing",
    }


def test_json_storage_missing_file_returns_default(tmp_path):
    assert JSONStorage(tmp_path / "missing.json").load(default={"ok": True}) == {"ok": True}


def test_json_storage_rejects_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(StorageError, match="Invalid JSON"):
        JSONStorage(path).load(default=[])


def test_json_storage_save_round_trip(tmp_path):
    path = tmp_path / "nested" / "results.json"
    storage = JSONStorage(path)
    storage.save({"score": 100})
    assert storage.load(default={}) == {"score": 100}


def test_question_repository_rejects_non_array(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps({"question": "wrong"}), encoding="utf-8")
    with pytest.raises(StorageError, match="JSON array"):
        QuestionRepository(path).load_questions()


def test_question_repository_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps([valid_question(1), valid_question(1)]), encoding="utf-8")
    with pytest.raises(StorageError, match="unique"):
        QuestionRepository(path).load_questions()


def test_question_repository_rejects_empty_bank(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(StorageError, match="empty"):
        QuestionRepository(path).load_questions()


def test_question_repository_loads_valid_questions(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps([valid_question()]), encoding="utf-8")
    questions = QuestionRepository(path).load_questions()
    assert len(questions) == 1
    assert questions[0].difficulty == Difficulty.BEGINNER


def test_result_repository_append(tmp_path):
    path = tmp_path / "results.json"
    repo = ResultRepository(path)
    repo.append({"name": "Ada", "score": 100})
    repo.append({"name": "Grace", "score": 80})
    assert repo.load_results() == [
        {"name": "Ada", "score": 100},
        {"name": "Grace", "score": 80},
    ]
