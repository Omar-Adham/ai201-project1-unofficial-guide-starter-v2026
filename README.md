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

Three runs of all five questions, caching off, on 2026-09-27. Raw output:
[`results/run_2026-09-27_1152_before.md`](results/run_2026-09-27_1152_before.md),
written by `run_eval.py::main`. Corpus `campus_life`, top-k 5, cutoff 0.52.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks read as complete thoughts | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Retrieval brings back 2+ useful chunks | 4 of 5 | 3/5 | 3/5 | 3/5 | MISSED |

**On the three columns being identical.** Four of my five criteria measure
stages with no model in them — chunking, embedding, retrieval, and a gate that
is a comparison against a fixed number — so they cannot vary between runs, and
reporting three different numbers would mean I had a bug, not better evidence.
The one criterion that runs through the model is criterion 2, and the three
runs there are visibly three separate calls: the same laundry question came
back as ``Source: `housing_old_brewhouse.txt` (also mentioned in ...)`` on run
1, ``Sources: `housing_old_brewhouse.txt` and ...`` on run 2, and a bare
parenthetical on run 3. `run_eval.py::run_once` passes `cache=False` for
exactly this reason, and `generate.py` reported 15 model calls for 5 questions
× 3 runs. The wording moved; the count didn't.

---

### Criterion 1 — retrieved chunk contains the answer: 4/5

Produced by `store.py::search`, called from `run_eval.py::run_once`. Four
questions retrieve a chunk holding the answer at rank 1. The fifth never
retrieves it at all:

```
Question: Which dining hall is open the latest?

#   distance   source                           preview
----------------------------------------------------------------------------
1   0.4215     dining_pellew_dining_hall_followup.txt Re: Pellew Dining Hall  Also worth saying: the furth...
2   0.4557     dining_pellew_dining_hall_followup.txt Re: Pellew Dining Hall  Adding to what people have s...
3   0.4564     dining_halden_hall_followup.txt  Re: Halden Hall  Also worth saying: closes at 7:00pm...
4   0.4920     dining_pellew_dining_hall.txt    Pellew Dining Hall  Second-year here. Wait times: 12...
5   0.4964     housing_aldridge_hall.txt        Aldridge Hall — what it's actually like  I lived her...

Gate: best distance 0.421 is under the 0.52 cutoff
```

The answer is Verrill Street Grill, open to 1:00am. `dining_verrill_street_grill.txt`
is not in the retrieved set, so no chunk containing the answer reaches the
model. This is the miss I said in criteria.md I expected, and for the reason I
said: the question needs closing times from all seven halls and TOP_K is 5.

The other four, from the same function:

```
How much does it cost to do laundry in Old Brewhouse?  → housing_old_brewhouse.txt        0.1464
What time does the salad bar wilt at Kestrel Commons?  → dining_kestrel_commons_followup.txt 0.1854
How late in the semester can I declare a course pass/fail? → admin_pass_fail_option.txt    0.2058
How often does the campus shuttle run at weekends?     → transit_shuttle.txt               0.1816
```

### Criterion 2 — every answer names a source: 5/5, three times over

Produced by `generate.py::answer_from_chunks`. All 15 answers named at least
one source document. One question across all three runs, to show both that it
cited every time and that the runs were genuinely separate:

```
### How much does it cost to do laundry in Old Brewhouse? — run 1
In Old Brewhouse, laundry costs $1.50 for a wash and $1.50 for a dry.

Source: `housing_old_brewhouse.txt` (also mentioned in `housing_old_brewhouse_laundry.txt`)

### How much does it cost to do laundry in Old Brewhouse? — run 2
In Old Brewhouse, laundry costs $1.50 for a wash and $1.50 for a dry.

Sources: `housing_old_brewhouse.txt` and `housing_old_brewhouse_laundry.txt`

### How much does it cost to do laundry in Old Brewhouse? — run 3
It costs $1.50 to wash and $1.50 to dry in Old Brewhouse (housing_old_brewhouse.txt and housing_old_brewhouse_laundry.txt).
```

Worth recording next to the 5/5: the dining hall answer cites a source and is
still wrong. It says Pellew, at 8:00pm, because Pellew is the latest hall *in
the chunks it was given*:

```
Pellew Dining Hall is open until 8:00pm daily, whereas Halden Hall closes at 7:00pm.

Source: `dining_pellew_dining_hall.txt` (and `dining_halden_hall_followup.txt`)
```

Criterion 2 asks whether answers name a source, and that one does. But it means
a citation is evidence of where an answer came from, not of whether it is
right — and my criteria have no target that would catch this. That belongs in
the Milestone 2 verdicts, so I am leaving it here as a note rather than
scoring it.

### Criterion 3 — gate stops out-of-corpus questions: 5/5

Produced by `run_eval.py::check_out_of_scope` at cutoff 0.52, one deterministic
pass. No model calls: a question the gate refuses never reaches the model.

```
Out-of-scope questions (the gate should refuse these):
  refused  (best distance 0.825)  What is the capital of Mongolia?
  refused  (best distance 0.923)  How do I change the oil in a diesel engine?
  refused  (best distance 0.886)  Who won the 1994 World Cup?
  refused  (best distance 0.848)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.877)  How do I write a for loop in Rust?
  -> gate refused 5 of 5
```

The closest of the five sits at 0.825, which is 0.305 clear of the cutoff —
the same separation I measured in Milestone 4 of unit 1, still holding after
re-chunking.

### Criterion 4 — chunks read as complete thoughts: 5/5

Produced by `chunker.py::split_documents`, sampled with `app.py::cmd_chunks`
(`python app.py chunks -n 5`). 159 chunks total, 5 sampled by stride. No
sentence is cut at either end of any of them:

```
Chunk 2  |  source: course_cs_340_exams.txt#1  |  produced by: chunker.py::split_documents
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.

Chunk 4  |  source: housing_aldridge_hall.txt#1  |  produced by: chunker.py::split_documents
Aldridge Hall — what it's actually like

The good: closest building to the science quad, four minutes to a 9am lab.

The bad: the elevator is out roughly one week per semester.

Chunk 5  |  source: housing_morrow_house.txt#3  |  produced by: chunker.py::split_documents
Morrow House — what it's actually like

Laundry costs $1.50 wash, $1.25 dry, coin or card. On noise: loud until about 1am on weekends, no enforced quiet hours.
```

Chunk 5 is the case I flagged in criteria.md when I wrote this target. Laundry
prices and noise levels are two different topics, glued together by the
merge-short-paragraphs rule. It passes the criterion as I wrote it — nothing is
cut mid-clause — so I am scoring it 5/5 rather than quietly marking it down
against a stricter rule I did not write. Whether the criterion is the right one
is a Milestone 2 question.

### Criterion 5 — retrieval brings back 2+ useful chunks: 3/5 — MISSED

Produced by `store.py::search` via `app.py::cmd_retrieve`. Counting chunks a
reader could actually use to answer the question, not chunks from a related
topic. Two questions return exactly one:

```
Question: How often does the campus shuttle run at weekends?

1   0.1816     transit_shuttle.txt              Runs a loop every 20 minutes from 7am to 11pm on weekdays
                                                and every 40 minutes on weekends.        ← the only useful one
2   0.5032     money_jobs.txt                   On-campus work. Maximum is 20 hours a week during term.
3   0.5443     study_library_hours.txt          Library hours. Open until 2am during term.
4   0.5447     dining_verrill_street_grill.txt  Verrill Street Grill. Wait times: up to 30 minutes on Friday
5   0.5503     transit_walking.txt              Walking times across campus. Add four minutes in winter.
```

```
Question: How late in the semester can I declare a course pass/fail?

1   0.2058     admin_pass_fail_option.txt       ...you can declare it as late as week eight  ← the only useful one
2   0.4293     admin_declaring_a_major.txt      You declare at the end of your second semester
3   0.4647     admin_add_drop_deadline.txt      You can add a course through the end of the second week
4   0.5371     admin_graduation_requirements.txt 120 credit hours, a completed major
5   0.5816     advising_registration.txt        Registration times are staggered by credit hours
```

Slots 2 through 5 are filled on distance alone in both cases. The shuttle
question pulls in on-campus jobs and a burger restaurant; the pass/fail
question pulls in four other administrative deadlines, none of which is the
pass/fail deadline. This is the same failure I described in criteria.md from
the housing lottery question, and it is still here.

The three that pass:

```
laundry in Old Brewhouse   housing_old_brewhouse.txt (0.1464) + housing_old_brewhouse_laundry.txt (0.2105)
                           — both give $1.50 wash, $1.50 dry
salad bar at Kestrel       dining_kestrel_commons_followup.txt (0.1854) + dining_kestrel_commons.txt (0.2594)
                           — both give "the salad bar wilts after 1:30"
which dining hall latest   dining_halden_hall_followup.txt (0.4564) "closes at 7:00pm"
                           + dining_pellew_dining_hall.txt (0.4920) "Hours are 7:00am to 8:00pm daily"
```

I want to be honest about the third one. It scores a pass because two chunks
carry dining hall closing times, which is the material this question needs.
Those same two chunks are what produced the wrong answer in criterion 2. So
this criterion counts a question as satisfied while the pipeline gets it wrong,
which tells me something about the criterion rather than about the retrieval.
Diagnosing that is Milestone 3; recording it is this.

## Verdicts

Scored against the targets in `criteria.md` as written in unit 1, not against
anything I rewrote after seeing the numbers.

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | **MET** | 4 of 5, which is the target exactly and not one more. Four questions return a chunk holding the answer at rank 1; the dining hall question never retrieves `dining_verrill_street_grill.txt` at all. No margin — one regression anywhere else and this is a miss. |
| 2 | Every answer names a source | **MET** | 15 of 15 answers named a source file, so 5/5 on all three runs. Not close, and the only argument against it is about what the criterion fails to ask, not about whether it held. |
| 3 | Gate stops out-of-corpus questions | **MET** | 5 of 5, every `OUT_OF_SCOPE` question refused with the nearest at 0.825 against a 0.52 cutoff. It is MET on the list the criterion names, and I am leaving it MET — but I found a question the gate does not stop, and I have revised the criterion rather than the verdict. See below. |
| 4 | Chunks read as complete thoughts | **MET** | MET under both readings of it, which is the problem: 5 of 5 by the criterion's own words, 4 of 5 by the reasoning I wrote underneath them. Revised for that, not for the score. |
| 5 | Retrieval brings back 2+ useful chunks | **MISSED** | 3 of 5 against a target of 4. The shuttle and pass/fail questions each return exactly one useful chunk out of five. A stricter reading gives 2 of 5; there is no reading that gives 4. |

### Where I argued myself out of a verdict, and where I didn't

**Criterion 1 — the tempting mistake is calling it a clean pass.** It is a pass,
but it is a pass with zero margin against a target I set *after* measuring
retrieval in unit 1, knowing this question would fail. I still think including
a question I knew would fail was the right call. But "4 of 5, target 4 of 5"
means this criterion currently cannot absorb a single regression, and I would
rather write that down now than discover it after the fix in Milestone 3.

I also checked the thing that would have let me off the hook: whether the
dining hall answer is even in the corpus. It is.

```
Hours are 11:00am to 1:00am daily during term.   dining_verrill_street_grill.txt
```

Seven dining halls, and Verrill closes at 1:00am against a next-latest of
9:00pm. The chunk exists and is never retrieved, so this is a retrieval
failure and not a corpus gap. That matters for Milestone 3: it means the fix
is in the retrieval stage, not in the documents.

**Criterion 2 — the argument against it is real but it is not an argument
about this criterion.** The strongest case is the dining hall answer: it cites
`dining_pellew_dining_hall.txt`, and it is wrong. If a citation can sit on a
wrong answer, what is 5/5 worth?

But I checked whether the citation was at least *accurate* for the claim it
made, and it is — Pellew's document does say 7:00am to 8:00pm. The answer is
wrong because the right document was never retrieved, not because the model
misattributed anything. Criterion 2 asks whether answers name a source. They
did, 15 times out of 15. What this shows is that my five criteria have no
target that catches a confident wrong answer, which is a gap in the *set* and
belongs in What I'd Do Differently — not a defect in criterion 2, and not a
reason to call a pass a fail.

**Criterion 5 — I tried to argue it up to 4 and could not.** The two ways to
get there both fail on the words I wrote. For the pass/fail question, the
add/drop chunk is a deadline, but it is a different deadline and it cannot
help you answer this one; the criterion explicitly excludes chunks that "came
from a related topic." For the shuttle question, walking times across campus
might inform whether you bother waiting, but they say nothing about how often
the shuttle runs.

Pushing the other way is easier. The dining hall question counts as a pass
because two chunks carry closing times — and those are the same two chunks
that produced the wrong answer. If "help answer it" means help reach the
*right* answer, this is 2 of 5. I scored it 3 because that is the more
generous reading and it still misses. A verdict that survives its own
best counter-argument is the one I trust.

### The number that surprised me

Not one from the run log. Criterion 3 came back 5 of 5 with a 0.3 margin, and
that looked too comfortable, so I wrote `tools/gate_probe.py` to push on it —
it runs the *near misses*, the plausible campus questions with no document
behind them, which `config.py` says are the ones that actually decide the
cutoff. Full output in
[`results/gate_probe_2026-09-27.txt`](results/gate_probe_2026-09-27.txt),
produced by `tools/gate_probe.py::main` over `store.py::search` and
`gate.py::check`. No model calls.

```
Near misses — no document behind them. The gate should refuse all.
  LET THROUGH  0.496  What are the gym opening hours?
               top chunk: health_center.txt
  refused      0.585  Is there a pharmacy on campus?
  refused      0.649  Can I keep a pet in my dorm room?
  refused      0.770  How do I join a student society?
  refused      0.580  Where do I go if I lose my student ID card?
  -> let 1 of 5 through
```

There is no gym document in this corpus — `grep -ril "gym"` over all 88
documents returns nothing. So the gate let through a question it should have
stopped, and handed the model the health centre's walk-in hours to answer a
question about a gym. That is the exact shape of a confident wrong answer.

Then the other side, which I only thought to run because criterion 3 counts
refusals and nothing else — meaning a gate that refuses *everything* scores a
perfect 5 of 5 on it:

```
Covered questions — a document exists. The gate should refuse none.
  REFUSED (wrongly)  0.527  Is there a campus health centre?
                     right doc at rank 1? yes
  answered           0.146  What are the walk-in hours at the health centre?
                     right doc at rank 1? yes
  -> wrongly refused 1 of 8
```

Those two questions are about **the same document**, and it is retrieved at
rank 1 for both. Asked as a specific fact it scores 0.146. Asked as a yes/no
existence question it scores 0.527 and gets refused. The distance is tracking
the shape of the question, not whether the corpus can answer it.

Now read the two probes together. The covered question sits at 0.527; the
uncovered gym question sits at 0.496. The one I should answer is *further
away* than the one I should refuse. They are in the wrong order, so no cutoff
anywhere separates them — moving the threshold trades one error for the other
and cannot fix both.

I spent unit 1 Milestone 4 tuning that threshold, and wrote 25 lines in
`config.py` justifying 0.52. I expected to find the number was slightly off. I
found that the number cannot do the job I was tuning it for.

## Diagnoses

Three things to diagnose, not one: criterion 5, which I missed outright; the
revised criterion 3, which I now fail; and the single miss inside criterion 1,
which passed but only because I had budgeted for exactly that failure.

Evidence for all three: [`results/rank_probe_2026-09-27.txt`](results/rank_probe_2026-09-27.txt)
(`tools/rank_probe.py`) and [`results/gate_probe_2026-09-27.txt`](results/gate_probe_2026-09-27.txt)
(`tools/gate_probe.py`). Neither makes a model call.

### The pattern, first

All three failures are the same defect showing up at two stages. **My pipeline
treats embedding distance as if it measured "does this chunk contain the
answer". It measures "is this chunk phrased like this question".** Every miss
is a place where those two come apart, and they come apart in both directions:

| | phrasing matches | phrasing doesn't match |
|---|---|---|
| **answer present** | the three questions that work | Verrill at rank 78; health centre refused at 0.527 |
| **answer absent** | gym question let through at 0.496 | correctly refused — the easy case `OUT_OF_SCOPE` tests |

The top-left is the only box my system handles, and it is the only box my
original criteria measured.

There is a sharper version of the pattern. Two of my failures are questions
that are not passage lookups at all:

- *"Which dining hall is open the latest?"* is a **comparison** — it needs
  seven closing times ordered against each other.
- *"Is there a campus health centre?"* is an **existence check** — it needs a
  yes/no about the whole corpus.

Neither is answerable by finding one passage that resembles the question, and
finding one passage that resembles the question is the only operation my
system has. That is one problem, not two, and no amount of tuning `TOP_K` or
`THRESHOLD` reaches it.

### Miss 1 — criterion 5, 3 of 5. Stage: **retrieval**

The mechanism is in one line. `gate.py::check`, line 57:

```python
best = min(r.distance for r in results)
```

The gate looks at the *single closest* chunk and then lets all five through.
`store.py::search` returns exactly `TOP_K` chunks whatever their distance.
So nothing anywhere in the pipeline inspects chunks 2 through 5 — they are
returned unconditionally, and the model is handed them as if they were
evidence.

That does no harm when the corpus holds five relevant chunks. It does exactly
this when it holds one:

```
How often does the campus shuttle run at weekends?
  0.1816  transit_shuttle.txt        ← the answer
  0.5032  money_jobs.txt             ← on-campus work hours
  0.5443  study_library_hours.txt
  0.5447  dining_verrill_street_grill.txt
  0.5503  transit_walking.txt
```

The distance profile says plainly that slots 2–5 are padding. Compare the
jump from rank 1 to rank 2 across all five questions:

| Question | rank 1 → rank 2 | criterion 5 |
|---|---|---|
| Which dining hall is open latest | 0.4215 → 0.4557 (**+0.03**) | pass |
| Laundry in Old Brewhouse | 0.1464 → 0.2105 (**+0.06**) | pass |
| Salad bar at Kestrel | 0.1854 → 0.2594 (**+0.07**) | pass |
| Pass/fail deadline | 0.2058 → 0.4293 (**+0.22**) | **fail** |
| Shuttle at weekends | 0.1816 → 0.5032 (**+0.32**) | **fail** |

The two failures are the two cliffs, and the separation is clean — 0.07
against 0.22. The cliff is the system telling me it ran out of relevant
material and kept going anyway, and nothing is reading that signal.

**Why those two questions and not the others.** This is the part I did not
expect. Only **7 of my 88 documents** have a `_followup` companion. Laundry
and Kestrel pass because they happen to sit in the redundant families — Old
Brewhouse has both a dorm document and a dedicated laundry document, Kestrel
has two followups. `transit_shuttle.txt` and `admin_pass_fail_option.txt` are
singletons; `ls transit*` returns two files for the entire transit topic.

So which questions pass criterion 5 is decided by whether their topic happened
to get a second document written about it. That is a property of the corpus,
not of anything I built.

**The uncomfortable consequence.** A relevance floor on chunks 2–5 is the
obvious fix and it will not move this criterion. It would correctly stop
returning `money_jobs.txt` for a shuttle question — but the shuttle answer
exists in exactly one chunk in the corpus, so filtering leaves one, and
criterion 5 demands two. The fix improves the answers and the criterion stays
missed.

The only way to get a second relevant chunk for the shuttle question is to
make one, by reinstating `CHUNK_OVERLAP` (currently 0) so the frequency
sentence lands in two adjacent chunks. That would satisfy the criterion's
letter with two chunks containing the same sentence, which is not what I meant
by "2 relevant chunks" when I wrote it. I am recording that here rather than
doing it, and choosing the fix in Milestone 4.

### Miss 2 — revised criterion 3. Stage: **embedding**

Same document, same rank 1, two ways of asking:

```
  answered           0.146  What are the walk-in hours at the health centre?
  REFUSED (wrongly)  0.527  Is there a campus health centre?
```

`health_center.txt` is retrieved at rank 1 for both. The distance moves by
**0.38 on the phrasing of the question alone**, while the corpus, the chunk
and the retrieval are identical. That is the whole diagnosis: the number the
gate reads is a function of how the question is worded, and the gate is being
asked to interpret it as whether the corpus can answer.

The mechanism is that `all-MiniLM-L6-v2` embeds a question near passages with
similar content words. "Walk-in hours" appears nearly verbatim in the
document. "Is there a..." has almost no content words to match — an existence
question is mostly grammar — so it drifts away from a document that is
entirely specifics.

The same mechanism causes the false pass. "What are the gym opening hours?" is
shaped exactly like an in-corpus hours question, so it lands 0.496 from the
health centre's opening hours despite there being **no gym document at all**
(`grep -ril "gym"` over 88 documents returns nothing).

And then the two errors sit in the wrong order: 0.496 for the question I
should refuse, 0.527 for the question I should answer. **There is no value of
`THRESHOLD` that separates them.** Every cutoff either lets the gym question
through or refuses the health centre question, or both. This is not a badly
chosen number; it is a number that cannot express the distinction, and I spent
unit 1 Milestone 4 and 25 lines of `config.py` choosing it.

### Also diagnosed — criterion 1's one miss. Stage: **embedding**, and my unit 1 diagnosis was wrong

Criterion 1 passed, so this is not a miss against a target. I am diagnosing it
because I wrote down a cause in unit 1 and it turns out to be false, which is
worth more than a diagnosis I got right.

In `criteria.md` I wrote: *"answering it needs the closing times of all seven
dining halls, and TOP_K is 5. Verrill was not in the top 5 at all."* True, and
it reads like a `TOP_K` problem. It is not:

```
Which dining hall is open the latest?
  answer should be in dining_verrill_street_grill.txt, containing '11:00am to 1:00am'
  -> rank 78 of 159   distance 0.7860   MISSED — outside TOP_K
     TOP_K would have to be 78 to reach it (49% of the corpus)
```

The answer chunk is in the **bottom half** of the corpus for the question it
answers, at 0.786 — further away than four of my five `OUT_OF_SCOPE` questions
about Mongolia and Rust. Raising `TOP_K` from 5 to 20 does nothing. Reaching
it means retrieving half the corpus, and at that point retrieval has stopped
being retrieval.

The mechanism: the chunk reads `Hours are 11:00am to 1:00am daily during
term.` The question asks which hall is open *latest*. Ordering 1:00am after
8:00pm is arithmetic, and embedding similarity has no arithmetic in it — the
two strings share no content words, so the model has no way to connect them.
The chunks that *do* come back are generic dining-hall prose, which resembles
a generic dining-hall question closely.

One correction to my own method while I am here. My first pass at this probe
searched for the string `1:00am` and reported a hit in `dining_north_kitchen.txt`
at rank 12, which would have suggested the answer was nearly retrieved. North
Kitchen closes at 7:00pm; the match was the `1:00am` inside `11:00am`. I now
match on document as well as text, and `tools/rank_probe.py` says why in its
docstring. The rank-78 figure is from the corrected probe.

### On the four I met

Four of five on the first try is the result that should make me suspicious,
and two of them do not survive a second look.

**Criterion 2 was set low and I would tighten it.** 15 of 15 was never in
doubt: the instruction to cite is sent twice, every chunk arrives labelled
with its filename, and nothing in the pipeline pushes the other way. I said so
in `criteria.md` when I set it. It is satisfied by the dining hall answer,
which cites a real document accurately and is wrong.

> **Would tighten to:** every answer names a source, **and** the claim it
> makes is supported by the document it cites — checked by reading the cited
> document, on all five questions.

I have not revised it in `criteria.md`, because it measured what it said it
measured and I only missed the fact that what it said was not worth much.
Lowering the bar is forbidden and raising it after the fact is not much
better, so it stays at 5 of 5 for this unit and the tightening is a proposal.

**Criterion 1 passed with zero margin against a target I set knowing this
question would fail**, and the failure is worse than the one I budgeted for —
rank 78 rather than rank 6. The target held, but it held over a hole.

Criteria 3 and 4 are revised in `criteria.md` with reasons. Criterion 5 is
the one I missed honestly.

## The Improvement

**What I changed:** hybrid retrieval. `store.py::search` now pulls 50
candidates from the vector store instead of 5, re-scores each one by blending
its embedding distance with a lexical score, and returns the best 5 of those.
The lexical half is in the new `lexical.py`; the blend is
`0.5 × semantic + 0.5 × (1 − coverage)`, where coverage is the IDF-weighted
fraction of the question's content words that appear in the chunk. One change,
in one stage: retrieval. Chunking, embedding, the prompt and `THRESHOLD` are
all untouched.

**Why I picked it:** my diagnosis said the gate could not separate *"what are
the gym opening hours?"* (0.496, no gym document exists) from *"is there a
campus health centre?"* (0.527, `health_center.txt` exists) because embedding
distance measures phrasing rather than coverage — and the word `gym` appears in
0 of 159 chunks, which is exactly the evidence a lexical signal has and an
embedding does not.

**Why not BM25, which is already in `requirements.txt`.** I tried it first. BM25
scores are unbounded and only meaningful relative to other chunks *for the same
query*, so blending one onto a distance scale means normalising per query — and
that hands the best chunk a perfect score whether it is a real match or the
least-bad of 159 irrelevant ones. The gym question would come out looking like a
direct hit, which is the precise failure I was trying to fix. IDF-weighted
coverage is absolute, so a query term that appears nowhere holds the score down
permanently. Full reasoning in `lexical.py`'s docstring.

**What I tested before building anything.** My first instinct was a second
chunking strategy — the Verrill document splits the phrase "the only late-night
hot food on campus" away from "Hours are 11:00am to 1:00am", so merging them
looked like it would rescue the dining hall question. I measured it before
writing it:

```
query: Which dining hall is open the latest?
  0.7860  current chunk: hours only (rank 78)
  0.7193  current chunk: prose only (has 'late-night')
  0.7299  MERGED whole document
  0.4919  for comparison — Pellew whole doc (currently wins at 0.4215)
```

Merging lands at 0.7299 — worse than the prose chunk alone, and nowhere near
Pellew. That fix would have failed, and I would have spent the 90 minutes
finding out.

### Run Log — After

`python run_eval.py --label after`, three runs, caching off, 15 model calls.
Raw output: [`results/run_2026-09-27_1223_after.md`](results/run_2026-09-27_1223_after.md).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | **4/5** | **MISSED** |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks read as complete thoughts | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Retrieval brings back 2+ useful chunks | 4 of 5 | **2/5** | **2/5** | **2/5** | **MISSED** |

Side by side:

| Criterion | Before | After | |
|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4/5 MET | 4/5 MET | unchanged |
| 2. Every answer names a source | 5/5 MET | 4/5 **MISSED** | **worse** |
| 3. Gate stops out-of-corpus questions | 5/5 MET | 5/5 MET | unchanged |
| 3-revised. Both sides of the gate | **FAILED** | **PASSES** | **better** |
| 4. Chunks read as complete thoughts | 5/5 MET | 5/5 MET | unchanged |
| 5. Retrieval brings back 2+ useful chunks | 3/5 MISSED | 2/5 **MISSED** | **worse** |

**Did it help?**

Yes on the failure I aimed at, and my scorecard got worse. Both of those are
real and they are the same event.

**What it fixed.** The revised criterion 3 — the one I wrote in Milestone 2 and
immediately failed — now passes both halves.
[`results/gate_probe_after_2026-09-27.txt`](results/gate_probe_after_2026-09-27.txt):

```
                     before          after
gym opening hours    0.496  through  0.683  refused     (no gym document exists)
campus health centre 0.527  refused  0.382  answered    (health_center.txt does)
near misses let through      1 of 5         0 of 5
covered wrongly refused      1 of 8         0 of 8
```

The inversion is gone. `THRESHOLD` is still 0.52 — I did not retune it, and
deliberately did not, because changing the scoring and the cutoff together
would have made it impossible to say which one moved the numbers.

**What it broke, and why the two are the same event.** Before, the dining hall
question produced this:

```
Pellew Dining Hall is open until 8:00pm daily, whereas Halden Hall closes at 7:00pm.
Source: `dining_pellew_dining_hall.txt` (and `dining_halden_hall_followup.txt`)
```

Confident, sourced, and **wrong** — Verrill Street Grill closes at 1:00am.
After:

```
I don't have enough information to determine which dining hall is open the
latest, as the provided documents only contain information for Pellew Dining
Hall.
```

That is the system getting better at the thing I most wanted it to be better
at, and **two of my five criteria score it as a regression.** Run 3's version
of that answer omits the filename, so criterion 2 drops to 4 of 5 and MISSES a
target it held 15 times out of 15 before. Criterion 5 drops from 3 of 5 to 2 of
5 because the dining question no longer retrieves Halden's closing time, so it
has one useful chunk instead of two.

My criteria reward confident coverage and penalise accurate refusal. I did not
know that until a change made the system more honest and the scorecard went
down.

**The mechanism behind the criterion 5 drop**, since "it got worse" is not a
diagnosis. Lexical coverage rewards chunks that repeat the question's words.
`Pellew Dining Hall` contains both "dining" and "hall"; `Re: Halden Hall`
contains only "hall". So hybrid scoring concentrated all five slots on the one
hall whose title best echoes the query:

```
                          before                          after
1  0.4215 pellew_followup        1  0.5100 pellew_followup
2  0.4557 pellew_followup        2  0.5272 pellew_followup
3  0.4564 halden_followup  ←     3  0.5453 pellew_dining_hall
4  0.4920 pellew_dining_hall     4  0.6359 innisfree_hall_noise
5  0.4964 aldridge_hall          5  0.6373 aldridge_hall_noise
```

Halden is gone. **Hybrid search helps single-fact lookup and hurts comparison
questions**, because a comparison needs breadth across documents and lexical
matching narrows onto whichever document echoes the query hardest. That is a
property of the fix, not a bug in it, and it is worth knowing.

The same narrowing helps elsewhere. The laundry question used to retrieve three
*other* dorms' laundry prices at ranks 3–5 — Calder at $2.00, Aldridge at $1.75,
Fenwick at $2.00 — next to Old Brewhouse's $1.50. All five chunks now come from
Old Brewhouse. Nothing in my criteria measures "stopped handing the model three
wrong prices for a question about one dorm", but it is the change I would most
want in a system students actually used.

**Where the dining hall answer still is.** Verrill moved from rank 78 to rank
**81** of 159 — slightly further away, because its hours chunk contains none of
"dining", "hall", "open" or "latest" and the lexical half therefore scores it
at zero. Criterion 1 holds at 4 of 5 for the same reason it did before. A
comparison question is not a passage lookup, and I have now confirmed that
twice with two different fixes.

**One process note.** Partway through this milestone every question started
being refused with nonsense top chunks, and I spent a while assuming my hybrid
code was wrong. It wasn't. I had run `tools/smoke_test.py`, which is a staff
tool that calls `build_index` with `AI201_FAKE_EMBEDDINGS=1` against the real
`config.CHROMA_DIR` — it had overwritten my index with stand-in vectors.
`python app.py index` restored it. I re-ran the before-numbers with
`AI201_HYBRID=0` afterwards and they reproduce exactly (0.496 and 0.527), which
is what tells me the after-numbers are comparable and not an artefact of the
rebuild.

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
