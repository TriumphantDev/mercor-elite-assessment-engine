import os
import json
import time
from datetime import datetime
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
RESULTS_FILE = os.path.join(BASE_DIR, "results.json")




def load_questions() -> list:
    with open(QUESTIONS_FILE, "r") as file:
        return json.load(file)


def save_result(result: dict) -> None:
   try:
    with open(RESULTS_FILE, "r") as file:
        data = json.load(file)
   except (FileNotFoundError, json.JSONDecodeError):
    data = []

    data.append(result)

    with open(RESULTS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def choose_difficulty() -> str:
    levels = ["Beginner", "Intermediate", "Advanced", "Elite"]

    print("\nSelect Difficulty:")
    for i, level in enumerate(levels, 1):
        print(f"{i}. {level}")

    while True:
        try:
            choice = int(input("Choose level: "))
            if 1 <= choice <= 4:
                return levels[choice - 1]
            else:
                print("Invalid range.")
        except ValueError:
            print("Enter a number.")


def evaluate(score: int, total: int) -> str:
    percent = (score / total) * 100

    if percent >= 95:
        return "MERCOR ELITE"
    elif percent >= 80:
        return "HIGH PERFORMER"
    elif percent >= 60:
        return "STRONG"
    elif percent >= 40:
        return "DEVELOPING"
    else:
        return "NEEDS IMPROVEMENT"


def show_leaderboard() -> None:
    if not os.path.exists(RESULTS_FILE):
        return

    with open(RESULTS_FILE, "r") as file:
        results = json.load(file)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print("\nLEADERBOARD")
    print("=" * 50)

    for r in results[:5]:
        print(f"{r['name']} | {r['difficulty']} | {r['score']}%")



def show_score_history(name: str) -> None:
    """
    Display historical performance analytics
    for a specific candidate.
    """

    if not os.path.exists(RESULTS_FILE):
        print("\nNo score history available.")
        return

    with open(RESULTS_FILE, "r") as file:
        results = json.load(file)

    history = [
        result for result in results
        if result["name"].lower() == name.lower()
    ]

    if not history:
        print("\nNo previous attempts found.")
        return

    print("\nSCORE HISTORY")
    print("=" * 60)

    total_score = 0
    best_score = 0

    for i, attempt in enumerate(history, 1):
        score = attempt["score"]
        total_score += score
        best_score = max(best_score, score)

        print(
            f"{i}. "
            f"{attempt['difficulty']} | "
            f"{score}% | "
            f"{attempt['time']}s | "
            f"{attempt['rating']}"
        )

    average_score = round(total_score / len(history), 2)

    print("\nPERFORMANCE ANALYTICS")
    print("-" * 60)
    print(f"Total Attempts: {len(history)}")
    print(f"Best Score: {best_score}%")
    print(f"Average Score: {average_score}%")

    if len(history) > 1:
        trend = history[-1]["score"] - history[0]["score"]

        if trend > 0:
            print(f"Trend: Improving (+{trend}%)")
        elif trend < 0:
            print(f"Trend: Declining ({trend}%)")
        else:
            print("Trend: Stable")
    else:
        print("Trend: Not enough data yet")


def ask_replay() -> bool:
    """
    Ask candidate whether to retake the assessment.
    Returns True if replay is requested.
    """

    while True:
        choice = input("\nReplay assessment? (y/n): ").strip().lower()

        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        else:
            print("Invalid input. Enter 'y' or 'n'.")


def run_test() -> None:
    questions = load_questions()

    print("\nMERCOR ELITE ASSESSMENT ENGINE")
    print("=" * 50)

    name = input("Enter candidate name: ")
    difficulty = choose_difficulty()

    filtered_questions = [
    q for q in questions if q["difficulty"] == difficulty
]

    random.shuffle(filtered_questions)

    score = 0
    start = time.time()

    for q in filtered_questions:
        print(f"\n[{difficulty}] {q['question']}")

        for i, option in enumerate(q["options"], 1):
            print(f"{i}. {option}")

        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(q["options"]):
                    break
                print("Invalid choice.")
            except ValueError:
                print("Enter a valid number.")

        selected = q["options"][choice - 1]

        if selected == q["answer"]:
            print("Correct")
            score += 1
        else:
            print(f"Wrong | Correct: {q['answer']}")

    end = time.time()

    duration = round(end - start, 2)
    percent = round((score / len(filtered_questions)) * 100, 2)
    rating = evaluate(score, len(filtered_questions))

    result = {
        "name": name,
        "difficulty": difficulty,
        "score": percent,
        "time": duration,
        "rating": rating,
        "timestamp": datetime.now().isoformat()
    }

    save_result(result)
    show_score_history(name)

    print("\nRESULTS")
    print("=" * 50)
    print(f"Candidate: {name}")
    print(f"Difficulty: {difficulty}")
    print(f"Score: {percent}%")
    print(f"Time: {duration}s")
    print(f"Rating: {rating}")

    show_leaderboard()


def main() -> None:
    """
    Main application lifecycle controller.
    """

    while True:
        run_test()

        if not ask_replay():
            print("\nExiting Mercor Elite Assessment Engine.")
            print("Session closed.")
            break


if __name__ == "__main__":
    main()