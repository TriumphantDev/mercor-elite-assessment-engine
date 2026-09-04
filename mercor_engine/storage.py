from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .models import Question


class StorageError(RuntimeError):
    pass


class JSONStorage:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, default: Any) -> Any:
        if not self.path.exists():
            return default
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Invalid JSON in {self.path}") from exc

    def save(self, data: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=self.path.name, suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)


class QuestionRepository:
    def __init__(self, path: str | Path):
        self.storage = JSONStorage(path)

    def load_questions(self) -> list[Question]:
        payload = self.storage.load(default=[])
        if not isinstance(payload, list):
            raise StorageError("Question bank must be a JSON array")
        questions = [Question.from_dict(item) for item in payload]
        ids = [question.id for question in questions]
        if len(ids) != len(set(ids)):
            raise StorageError("Question IDs must be unique")
        if not questions:
            raise StorageError("Question bank is empty")
        return questions


class ResultRepository:
    def __init__(self, path: str | Path):
        self.storage = JSONStorage(path)

    def load_results(self) -> list[dict[str, Any]]:
        payload = self.storage.load(default=[])
        if not isinstance(payload, list):
            raise StorageError("Results file must be a JSON array")
        return payload

    def append(self, result: dict[str, Any]) -> None:
        results = self.load_results()
        results.append(result)
        self.storage.save(results)
