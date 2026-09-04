from mercor_engine.analytics import candidate_history, leaderboard, summarize_history, weak_categories


def test_candidate_history_is_case_insensitive():
    results = [{"name": "Ada", "score": 80}, {"name": "Grace", "score": 90}]
    assert candidate_history(results, "ada") == [results[0]]


def test_summarize_history_empty():
    assert summarize_history([]) == {
        "attempts": 0,
        "best_score": 0,
        "average_score": 0,
        "trend": "No data",
    }


def test_summarize_history_improving_and_declining():
    improving = summarize_history([{"score": 60}, {"score": 80}])
    declining = summarize_history([{"score": 80}, {"score": 60}])
    assert improving["trend"] == "Improving"
    assert improving["trend_delta"] == 20
    assert declining["trend"] == "Declining"
    assert declining["trend_delta"] == -20


def test_weak_categories_uses_threshold():
    assert weak_categories({"Python": 69.9, "Algorithms": 70, "SQL": 50}) == ["Python", "SQL"]


def test_leaderboard_orders_score_then_duration_then_timestamp():
    results = [
        {"name": "Slow", "score": 100, "duration_seconds": 30, "timestamp": "2026-01-02"},
        {"name": "Fast", "score": 100, "duration_seconds": 20, "timestamp": "2026-01-03"},
        {"name": "Early", "score": 100, "duration_seconds": 20, "timestamp": "2026-01-01"},
        {"name": "Lower", "score": 90, "duration_seconds": 1, "timestamp": "2026-01-01"},
    ]
    ranked = leaderboard(results)
    assert [item["name"] for item in ranked] == ["Early", "Fast", "Slow", "Lower"]


def test_leaderboard_limit():
    assert len(leaderboard([{"score": score} for score in range(10)], limit=3)) == 3
