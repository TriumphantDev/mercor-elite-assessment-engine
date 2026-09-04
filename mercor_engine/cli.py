from __future__ import annotations

from pathlib import Path

from .analytics import candidate_history, leaderboard, summarize_history, weak_categories
from .engine import AdaptiveAssessmentEngine, AssessmentConfig
from .models import Difficulty, Question
from .storage import QuestionRepository, ResultRepository, StorageError


def ask_int(prompt: str, minimum: int, maximum: int) -> int:
    while True:
        try:
            value = int(input(prompt))
            if minimum <= value <= maximum:
                return value
        except ValueError:
            pass
        print(f"Enter a number from {minimum} to {maximum}.")


def choose_difficulty() -> Difficulty:
    levels = list(Difficulty)
    print("\nStarting difficulty")
    for level in levels:
        print(f"{int(level)}. {level.label}")
    return Difficulty(ask_int("Choose: ", 1, len(levels)))


def answer_provider(question: Question, index: int) -> str:
    options = question.options[:]
    print(f"\nQuestion {index + 1} | {question.category} | {question.difficulty.label}")
    print(question.question)
    for position, option in enumerate(options, 1):
        print(f"{position}. {option}")
    choice = ask_int("Answer: ", 1, len(options))
    selected = options[choice - 1]
    if selected == question.answer:
        print("Correct.")
    else:
        print(f"Incorrect. Correct answer: {question.answer}")
    if question.explanation:
        print(f"Why: {question.explanation}")
    return selected


def print_result(result) -> None:
    print("\n" + "=" * 60)
    print("ASSESSMENT COMPLETE")
    print("=" * 60)
    print(f"Candidate: {result.name}")
    print(f"Score: {result.score}% ({result.correct_answers}/{result.total_questions})")
    print(f"Rating: {result.rating}")
    print(f"Duration: {result.duration_seconds}s")
    print(f"Difficulty: {result.starting_difficulty} -> {result.ending_difficulty}")
    print("Category performance:")
    for category, score in sorted(result.category_accuracy.items()):
        print(f"  - {category}: {score}%")
    weak = weak_categories(result.category_accuracy)
    if weak:
        print("Focus areas: " + ", ".join(weak))


def run(base_dir: Path | None = None) -> None:
    base_dir = base_dir or Path(__file__).resolve().parent.parent
    questions_path = base_dir / "questions.json"
    results_path = base_dir / "results.json"
    try:
        questions = QuestionRepository(questions_path).load_questions()
        result_repo = ResultRepository(results_path)
    except StorageError as exc:
        print(f"Storage error: {exc}")
        return

    print("\nMERCOR ELITE ASSESSMENT ENGINE V2")
    name = input("Candidate name: ").strip() or "Anonymous"
    difficulty = choose_difficulty()
    max_questions = min(len(questions), 10)
    count = ask_int(f"Questions (1-{max_questions}): ", 1, max_questions)

    engine = AdaptiveAssessmentEngine(questions)
    result = engine.run(name, answer_provider, AssessmentConfig(question_count=count, starting_difficulty=difficulty))
    result_repo.append(result.to_dict())
    print_result(result)

    all_results = result_repo.load_results()
    history = candidate_history(all_results, name)
    summary = summarize_history(history)
    print("\nPERSONAL HISTORY")
    print(f"Attempts: {summary['attempts']} | Best: {summary['best_score']}% | Average: {summary['average_score']}% | Trend: {summary['trend']}")

    print("\nLEADERBOARD")
    for position, entry in enumerate(leaderboard(all_results), 1):
        print(f"{position}. {entry.get('name')} — {entry.get('score')}% | {entry.get('rating', 'N/A')}")


def main() -> None:
    while True:
        run()
        if input("\nRun another assessment? (y/n): ").strip().lower() not in {"y", "yes"}:
            print("Session closed.")
            break
