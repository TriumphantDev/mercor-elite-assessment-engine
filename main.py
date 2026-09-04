"""Backward-compatible entry point for Mercor Elite Assessment Engine V2."""

from mercor_engine.cli import main
from mercor_engine.engine import AdaptiveAssessmentEngine


def evaluate(score: int, total: int) -> str:
    """Return the legacy rating for a score/total pair."""
    percentage = (score / total * 100) if total else 0
    return AdaptiveAssessmentEngine.rating(percentage)


if __name__ == "__main__":
    main()
