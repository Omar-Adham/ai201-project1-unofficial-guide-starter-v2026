# The Unofficial Guide

**Name:** Omar Ibrahim Adham

**Corpus:** `campus_life` — 88 short posts about student life.

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

**Question:** How much does it cost to do laundry in Old Brewhouse?

**Answer:**

```
  (best distance 0.146, cutoff 0.52)

Laundry in Old Brewhouse costs $1.50 to wash and $1.50 to dry.

This information came from `housing_old_brewhouse.txt` and `housing_old_brewhouse_laundry.txt`.

Sources retrieved: housing_aldridge_hall.txt, housing_calder_annexe.txt,
housing_fenwick_court_laundry.txt, housing_old_brewhouse.txt,
housing_old_brewhouse_laundry.txt
```

I picked this one because three of the five chunks it retrieved were laundry
prices for the *wrong* buildings — Calder Annexe at $2.00/$1.75, Aldridge Hall
at $1.75/$1.50, Fenwick Court at $2.00/$1.75 — and the answer is still right.
That is the title prefix from Milestone 3 doing its job: every chunk names its
own building, so the model can tell which price belongs to the question.

And the refusal, for contrast:

```
  (best distance 0.886, cutoff 0.52)

I don't have enough information about that.
```

**My relevance cutoff:** 0.52

I measured three groups, not two, and the third one is what moved the number.

| Question | In corpus? | Best distance |
|---|---|---|
| How much does it cost to do laundry in Old Brewhouse? | yes | 0.146 |
| How often does the campus shuttle run at weekends? | yes | 0.182 |
| What time does the salad bar wilt at Kestrel Commons? | yes | 0.185 |
| How late in the semester can I declare a course pass/fail? | yes | 0.206 |
| Which dining hall is open the latest? | yes | 0.421 |
| What are the opening hours of the campus gym? | no — near miss | 0.382 |
| Where is the nearest pharmacy to campus? | no — near miss | 0.612 |
| What is the policy on keeping pets in the dorms? | no — near miss | 0.639 |
| How do I appeal a parking ticket? | no — near miss | 0.657 |
| What counts as plagiarism here? | no — near miss | 0.762 |
| How do I join a student society? | no — near miss | 0.770 |
| What is the capital of Mongolia? | no | 0.825 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.848 |
| How do I write a for loop in Rust? | no | 0.877 |
| Who won the 1994 World Cup? | no | 0.886 |
| How do I change the oil in a diesel engine? | no | 0.923 |

**What the groups looked like.** My five questions ran 0.146 to 0.421. The
five `OUT_OF_SCOPE` questions ran 0.825 to 0.923. On those two groups alone
the gap is enormous — 0.42 to 0.83, with nothing in it — and almost any number
in the middle would have looked justified.

That gap is an artefact of the `OUT_OF_SCOPE` questions being about Mongolia,
Rust and diesel engines. Nobody asks this system those. So I wrote six
questions a student would plausibly ask that my corpus has no document for,
and they land between 0.382 and 0.770 — **inside** the gap.

**Why 0.52.** The real decision window is between my hardest true question
(0.421) and my closest near miss (0.612). 0.52 is the middle of it, leaving
about 0.10 of margin on each side. The shipped 0.6 sat only 0.012 below that
pharmacy question, which is not margin at all — one more near-miss question
and it would have been answered from the walking-times document.

**What I get wrong at 0.52.** "What are the opening hours of the campus gym?"
scores 0.382 and passes the gate. That is *lower* than my hardest real
question, so no threshold anywhere can separate the two — lowering the cutoff
far enough to refuse the gym question would also refuse the dining hall one.
This is the case the gate cannot catch, and it is exactly the case the
grounding instruction exists for. I ran it end to end to check:

```
  (best distance 0.382, cutoff 0.6)

I don't have enough information to answer your question as the opening hours
of the campus gym are not mentioned in the provided documents.
```

The gate passed it and the second layer refused it. That is the reason for
having two layers rather than one, and it is why I left `GROUNDING_INSTRUCTION`
alone rather than tightening it — I tested it against the case it exists for
and it held.

**Why TOP_K stays at 5.** I tried 8 and 12 on the dining hall question, which
is the one that needs to see more documents than it does. Neither helped:
Verrill Street Grill, which closes at 1:00am and is the correct answer, is not
retrieved at any top-k I tried. The embedding does not connect "latest" to
"1:00am". Everything the larger top-k added was dorm descriptions, so raising
it would cost precision and buy nothing.

## How I Used AI

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

**2. Setting the relevance cutoff (Milestone 4).** This one changed my answer,
not just my code. I had my two groups of distances — 0.146 to 0.421 for my
questions, 0.825 to 0.923 for the `OUT_OF_SCOPE` ones — and I asked where the
cutoff should go and what I would get wrong at that number. The second half of
that question is what produced something useful.

What came back was that the gap looked clean because the questions making it
were about Mongolia, Rust and diesel engines, and nobody asks this system
those. The suggestion was to measure a third group: questions a student would
plausibly ask that my corpus has no document for. I wrote six — gym hours,
pharmacies, pets in dorms, joining a society, appealing a parking ticket,
plagiarism — and they came out between 0.382 and 0.770, inside the gap I was
about to put a number in the middle of.

That moved my cutoff from 0.6 to 0.52, and it exposed a case I would not have
found otherwise: the gym question scores 0.382, which is *lower* than my
hardest real question, so no threshold can separate them. I checked what
happened to it end to end, and the grounding instruction refused it after the
gate had let it through. That is why I left `GROUNDING_INSTRUCTION` alone
instead of tightening it — I had a real example of it doing the job, so
tightening it would have been guessing.

**Also worth recording.** I had my five acceptance criteria pressure-tested by
asking how each one would be tested using only what the sentence said, with no
improvements suggested. Criterion 2 came back with a hole I had not thought
about: a question the gate refuses produces no source, so does a refusal count
against "every answer names a source"? Nothing in my sentence said. I did not
rewrite the criterion, since it was given to me, but I wrote the answer into
my reasoning underneath it. I also had my five test questions checked against
the corpus before committing to them — all five came back answerable at rank 1,
which would have made "4 of 5" a target I could not miss, so I replaced the
MATH 220 lookup with the dining hall question that genuinely fails.

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
