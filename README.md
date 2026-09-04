# Mercor Elite Assessment Engine V2

A modular Python assessment platform with **adaptive difficulty**, category analytics, persistent attempt history, and automated quality checks.

## What changed in V2

The original CLI selected one difficulty and filtered questions to that level. V2 introduces a real adaptive engine: consecutive correct answers promote the candidate, while consecutive incorrect answers lower difficulty. Every attempt records the difficulty journey and category-level performance.

### Features

- Adaptive difficulty progression
- Configurable question counts and adaptation thresholds
- Validated JSON question bank
- Question categories and explanations
- Per-category accuracy and focus-area detection
- Persistent attempt history
- Leaderboard with deterministic tie-breaking
- Atomic JSON writes to reduce partial-file corruption
- Backward-compatible `main.py` entry point
- Pytest test suite
- Ruff linting and GitHub Actions CI

## Architecture

```text
mercor-elite-assessment-engine/
├── main.py                     # compatibility entry point
├── questions.json              # question bank
├── results.json                # local runtime data
├── pyproject.toml
├── mercor_engine/
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py               # domain models
│   ├── engine.py               # adaptive assessment logic
│   ├── analytics.py            # history and leaderboard logic
│   ├── storage.py              # validated atomic JSON persistence
│   └── cli.py                  # terminal experience
├── tests/
│   └── test_engine.py
└── .github/workflows/ci.yml
```

## Adaptive rules

The default configuration starts at a selected level.

- **2 consecutive correct answers**: promote one difficulty level
- **2 consecutive incorrect answers**: demote one difficulty level
- Difficulty is bounded between **Beginner** and **Elite**
- Questions are not repeated within an attempt
- If the exact difficulty pool is exhausted, the engine falls back to any unused question so an assessment can continue

## Difficulty levels

| Level | Typical focus |
|---|---|
| Beginner | Core Python fundamentals |
| Intermediate | Applied Python and data structures |
| Advanced | Algorithms and design concepts |
| Elite | Python internals and software engineering trade-offs |

## Installation

```bash
git clone https://github.com/TriumphantDev/mercor-elite-assessment-engine.git
cd mercor-elite-assessment-engine
python -m pip install -e ".[dev]"
```

Run either command:

```bash
python main.py
# or
python -m mercor_engine
```

Run quality checks:

```bash
ruff check .
pytest -q
```

## Example result data

Each V2 attempt stores score, duration, rating, starting and ending difficulty, the difficulty path, category accuracy, and per-question outcomes. This makes the data useful for future dashboards or SQLite/PostgreSQL migration.

## Performance classification

| Score | Classification |
|---|---|
| 95–100% | MERCOR ELITE |
| 80–94% | HIGH PERFORMER |
| 60–79% | STRONG |
| 40–59% | DEVELOPING |
| Below 40% | NEEDS IMPROVEMENT |

## Next evolution

Potential V3 directions:

- SQLite or PostgreSQL persistence
- Timed questions
- Negative marking modes
- Candidate authentication
- FastAPI backend
- Web dashboard and recruiter analytics
- Larger domain-specific question banks
- Item difficulty calibration and richer adaptive algorithms

## Development principles

V2 keeps the core assessment logic independent from the CLI and storage layers. That separation makes the engine testable, reusable from a future API, and easier to evolve without rewriting the business logic.
