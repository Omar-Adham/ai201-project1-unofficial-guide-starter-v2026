#!/usr/bin/env python3
"""
Probe the relevance gate from both sides.

    python tools/gate_probe.py

`run_eval.py` scores criterion 3 by running `OUT_OF_SCOPE` through the gate and
counting refusals. That measures one side of one easy case, and in unit 2 it
turned out to be hiding two things:

  1. The `OUT_OF_SCOPE` questions are about Mongolia and Rust. The questions
     that actually sit near the cutoff are *near misses* — plausible campus
     questions with no document behind them. Those are what decide whether a
     cutoff is in the right place.

  2. Counting only refusals means a gate that refuses everything scores
     perfectly. The other side — questions the corpus does cover, wrongly
     refused — is invisible to it.

This runs both sides. No model calls: retrieval and the gate are all it
touches, so it costs nothing to run as often as you like.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import gate  # noqa: E402
from store import search  # noqa: E402

# Plausible campus questions this corpus has no document for. The gate should
# refuse every one of these, and they are much harder than OUT_OF_SCOPE.
#
# Each one is checked against the corpus before it goes in this list. `gym`,
# `pharmac`, `pet` and `societ` return nothing at all from a case-insensitive
# grep over all 88 documents. The other two need a closer look and still
# qualify: "club" appears once, in `orientation_what_matters.txt`, and only to
# say the club fair runs too long — it does not say how to join one. "student
# ID" appears once, in `transit_shuttle.txt`, and only to say the shuttle is
# free with one — nothing about losing it.
#
# "Is there a campus health centre?" was in this list until I checked it the
# same way. `health_center.txt` exists, so it is a covered question, and it is
# in COVERED below instead. The gate refuses it anyway, which is the point.
NEAR_MISSES = [
    "What are the gym opening hours?",
    "Is there a pharmacy on campus?",
    "Can I keep a pet in my dorm room?",
    "How do I join a student society?",
    "Where do I go if I lose my student ID card?",
]

# Questions with a document behind them. The gate should refuse none of these.
# Deliberately asked in two shapes: yes/no existence questions and
# specific-fact questions, because that turned out to be the thing that moves
# the distance most.
COVERED = [
    ("Is there a campus health centre?", "health_center.txt"),
    ("What are the walk-in hours at the health centre?", "health_center.txt"),
    ("When is the add/drop deadline?", "admin_add_drop_deadline.txt"),
    ("How many credit hours do I need to graduate?", "admin_graduation_requirements.txt"),
    ("How late is the library open during term?", "study_library_hours.txt"),
    ("How much does laundry cost in Morrow House?", "housing_morrow_house.txt"),
    ("Is Aldridge Hall noisy?", "housing_aldridge_hall.txt"),
    ("How many hours a week can I work on campus?", "money_jobs.txt"),
]


def probe(question):
    results = search(question, top_k=config.TOP_K, corpus=config.CORPUS)
    decision = gate.check(results, threshold=config.THRESHOLD)
    top = results[0].source if results else "-"
    return decision, top


def main():
    print(f"Gate probe — cutoff {config.THRESHOLD}, corpus {config.CORPUS}\n")

    print("Near misses — no document behind them. The gate should refuse all.")
    let_through = 0
    for question in NEAR_MISSES:
        decision, top = probe(question)
        if decision.passed:
            let_through += 1
        mark = "LET THROUGH" if decision.passed else "refused"
        print(f"  {mark:<12} {decision.best_distance:.3f}  {question}")
        print(f"               top chunk: {top}")
    print(f"  -> let {let_through} of {len(NEAR_MISSES)} through\n")

    print("Covered questions — a document exists. The gate should refuse none.")
    wrongly_refused = 0
    for question, expected in COVERED:
        decision, top = probe(question)
        if not decision.passed:
            wrongly_refused += 1
        mark = "REFUSED (wrongly)" if not decision.passed else "answered"
        hit = "yes" if top == expected else f"no -> {top}"
        print(f"  {mark:<18} {decision.best_distance:.3f}  {question}")
        print(f"                     right doc at rank 1? {hit}")
    print(f"  -> wrongly refused {wrongly_refused} of {len(COVERED)}")

    if let_through and wrongly_refused:
        print(
            "\nBoth kinds of error at once. Moving the cutoff trades one for the\n"
            "other — it cannot fix both, because at least one covered question\n"
            "sits further away than at least one uncovered question."
        )


if __name__ == "__main__":
    main()
