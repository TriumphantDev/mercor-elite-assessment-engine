from __future__ import annotations

from collections import defaultdict
from typing import Any


def candidate_history(results: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [result for result in results if result.get("name", "").casefold() == name.casefold()]


def summarize_history(history: list[dict[str, Any]]) -> dict[str, Any]:
    if not history:
        return {"attempts": 0, "best_score": 0, "average_score": 0, "trend": "No data"}
    scores = [float(item.get("score", 0)) for item in history]
    trend = scores[-1] - scores[0] if len(scores) > 1 else 0
    return {
        "attempts": len(scores),
        "best_score": max(scores),
        "average_score": round(sum(scores) / len(scores), 2),
        "trend": "Improving" if trend > 0 else "Declining" if trend < 0 else "Stable",
        "trend_delta": round(trend, 2),
    }


def weak_categories(category_accuracy: dict[str, float], threshold: float = 70) -> list[str]:
    return sorted(category for category, score in category_accuracy.items() if score < threshold)


def leaderboard(results: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(
        results,
        key=lambda item: (-float(item.get("score", 0)), float(item.get("duration_seconds", item.get("time", 0))), item.get("timestamp", "")),
    )
    return ranked[:limit]
