#!/usr/bin/env python3
"""
Where does the answer-bearing chunk actually rank?

    python tools/rank_probe.py

`app.py retrieve` shows you the top 5. That is enough to tell you a question
failed, and not enough to tell you why, because it cannot distinguish:

    rank 6   — the chunk is nearly there. Raising TOP_K fixes it.
    rank 78  — the embedding does not think this chunk answers this question.
               No value of TOP_K worth having fixes it.

Those are failures at different stages and they want different fixes, so this
asks for the whole corpus ranked and reports where the answer landed.

Each probe names the source document the answer lives in as well as the text
to look for, because a bare substring lies: searching for "1:00am" also
matches "11:00am", which is how North Kitchen (closes 7:00pm) first showed up
as a hit on a question about the latest-closing dining hall.

No model calls.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from store import search  # noqa: E402

# (question, text the answering chunk must contain, document it should be in)
PROBES = [
    (
        "Which dining hall is open the latest?",
        "11:00am to 1:00am",
        "dining_verrill_street_grill.txt",
    ),
    (
        "How often does the campus shuttle run at weekends?",
        "every 40 minutes on weekends",
        "transit_shuttle.txt",
    ),
    (
        "How late in the semester can I declare a course pass/fail?",
        "as late as week eight",
        "admin_pass_fail_option.txt",
    ),
    (
        "Is there a campus health centre?",
        "Walk-in hours",
        "health_center.txt",
    ),
]


def main():
    print(f"Rank probe — corpus {config.CORPUS}, TOP_K in use is {config.TOP_K}\n")

    for question, needle, document in PROBES:
        # Ask for everything, not TOP_K.
        results = search(question, top_k=10_000, corpus=config.CORPUS)
        print("=" * 74)
        print(question)
        print(f"  answer should be in {document}, containing {needle!r}")
        print(f"  {len(results)} chunks ranked")

        hits = [
            (i, r)
            for i, r in enumerate(results, 1)
            if needle in r.text and r.source == document
        ]
        if not hits:
            print("  the answer is in NO chunk anywhere — a corpus problem, not a")
            print("  retrieval one")
        for rank, r in hits:
            verdict = "inside TOP_K" if rank <= config.TOP_K else "MISSED — outside TOP_K"
            print(f"  -> rank {rank} of {len(results)}   distance {r.distance:.4f}   {verdict}")
            if rank > config.TOP_K:
                print(f"     TOP_K would have to be {rank} to reach it "
                      f"({rank / len(results):.0%} of the corpus)")
        print()


if __name__ == "__main__":
    main()
