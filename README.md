# The Unofficial Guide

**Corpus:** `campus_life` — 88 short posts about student life.

<!-- ⚠️ TODO: put your name on the line above. I left it off deliberately
     rather than guess it. -->


> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This answers questions about student life at a university, using the
`campus_life` corpus: 88 short posts, one to three paragraphs each, covering
dorms, dining halls, course workloads and the administrative rules nobody
explains properly. You ask a question in plain English, it finds the handful
of passages most likely to contain the answer, and a language model writes the
answer from those passages and names the file it used.

It is built for specific, factual questions — "how much does laundry cost in
Old Brewhouse", "how late can I declare a course pass/fail" — rather than for
open-ended ones. It is deliberately bad at questions that require comparing
every document in the corpus, because it only ever looks at five of them at a
time. If nothing relevant comes back, it refuses rather than guessing.

## Chunking Strategy

**Chunk size:** 500 characters — a ceiling, not a target
**Overlap:** 0

I split on paragraph breaks and repeat the document's title on every chunk.
Neither number above is what decides where a chunk ends.

**Why not a character count.** The starter cut at 800 characters with 120 of
overlap. My documents run 178 to 549 characters, so it never cut anything:
88 documents came out as 88 chunks. That is not a bug, but it is not the right
answer either, because most of these documents hold more than one thought.
`dining_kestrel_commons.txt` has one paragraph about wait times and the
stir-fry station, and a second about opening hours and price. Asking about
hours had to match against the wait-time sentences too, and they diluted it.

**Why the title gets repeated.** All 88 documents put their title alone on the
first line. That creates two problems at once. Splitting on blank lines
naively gives every document a 22-character orphan chunk reading
`"On the housing lottery"` and nothing else. And the body paragraphs mostly
don't name their own subject — `"Hours are 7:00am to 9:00pm weekdays"` appears
with the words "Kestrel Commons" nowhere in it. This corpus has seven dining
halls and seven laundry rooms written to the same template, and two of the
laundry documents share entire sentences word for word, so a chunk that
doesn't name its building is a chunk that gets retrieved for the wrong one.

Treating the title as a prefix rather than as a chunk solves both.

**Why zero overlap.** Overlap exists so that a thought cut in half survives
whole in one of the two pieces. Splitting on paragraph breaks means nothing
gets cut in half, so there is nothing for it to rescue. The context these
documents actually need carried across is *which building this is about*, and
the repeated title carries that directly — 120 characters of the previous
paragraph would not.

**What changed:**

| | Starter (`fallback_split`) | Mine (`split_documents`) |
|---|---|---|
| Chunks | 88 | 159 |
| Average length | 317 | 188 |
| Shortest | 178 | 103 |
| Longest | 549 | 397 |

Retrieval distances improved on four of my five test questions, most sharply
on the shuttle question (0.412 → 0.182), where the weekend frequency had been
buried in a chunk that also covered timetable accuracy and which stop gets
skipped. One question was unchanged (`admin_pass_fail_option.txt` is a single
paragraph, so there was nothing to split).

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

From `python app.py chunks -n 5`, on 159 chunks.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — produced by: `chunker.py::split_documents`

```
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_stat_150_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for STAT 150 Applied Statistics

People keep asking so: 5 to 6 hours a week outside class. That's real time, not optimistic time.
```

**Chunk 4** — source: `housing_aldridge_hall.txt#1` — produced by: `chunker.py::split_documents`

```
Aldridge Hall — what it's actually like

The good: closest building to the science quad, four minutes to a 9am lab.

The bad: the elevator is out roughly one week per semester.
```

**Chunk 5** — source: `housing_morrow_house.txt#3` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like

Laundry costs $1.50 wash, $1.25 dry, coin or card. On noise: loud until about 1am on weekends, no enforced quiet hours.
```

All five answer a question without needing the text around them, and none
begins or ends mid-sentence. Chunk 5 is the one that shows why the title
prefix matters: `$1.50 wash` is a price that four other buildings in this
corpus also charge something similar for, and without `Morrow House` at the
top it would be retrievable for any of them.

Chunk 2 is the shortest of the five at 103 characters and is the one I looked
hardest at. It is a single piece of advice, it names its course, and it
answers "when should I start the CS 340 project" on its own — so I kept it.
My `MIN_CHUNK` of 80 characters is what stops anything genuinely smaller than
that from surviving as its own chunk.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**

```
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1. Writing the chunker (Milestone 3).** I used Claude Code for this, and it
wrote the code in `chunker.py::split_documents`. What I asked for was a
chunking strategy fitted to `campus_life` rather than a generic one. What came
back first was the obvious answer — split on blank lines — but it checked that
against the corpus before writing it and found the thing that makes the
obvious answer wrong: all 88 documents put their title alone on the first
line, so a blank-line split would have produced 88 orphan chunks reading
`"On the housing lottery"` and nothing else. The strategy changed to treating
the title as a prefix repeated on every chunk instead of as a chunk. That
turned out to matter for a second reason neither of us started with — seven
dining halls and seven laundry rooms are written to the same template, two
laundry documents share whole sentences verbatim, and a chunk saying
`"Laundry costs $1.50 wash"` with no building name is retrievable for any of
them.

The thing I had to push back on was the first version of the code, which
assigned chunk indices from the paragraph loop while the oversized-paragraph
branch assigned them from a separate count. On `campus_life` nothing is long
enough to reach that branch so it never fired, but a document with one long
paragraph followed by a short one would have produced two chunks with the
same index. I had it restructured around a single running counter.

**2. Pressure-testing my acceptance criteria (Milestone 2).** I pasted my five
criteria in and asked how each one would be tested using only what the
sentence said, with no improvements suggested. Three came back testable.
Criterion 5 came back as the weakest, because "relevant" was doing all the
work and two people would score the same chunk differently. Criterion 2 came
back with a hole I had not thought about: a question the gate refuses produces
no source, so does a refusal count as a failure of "every answer names a
source"? Nothing in my sentence said. I did not rewrite the criterion, since
it was given to me, but I wrote the answer into my reasoning underneath it —
refusals are not counted here, because that is what criterion 3 measures and
one event should not fail two criteria.

I also had my five test questions checked against the corpus before committing
to them. All five came back answerable at rank 1, which meant a target of
"4 of 5" would have been one I could not miss. I replaced the MATH 220
workload lookup with "Which dining hall is open the latest?", which is
genuinely unanswerable by this pipeline — the answer is Verrill Street Grill
and Verrill is not in the retrieved set.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
