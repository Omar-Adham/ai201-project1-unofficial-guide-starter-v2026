# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

<!-- Evidence you have for this, from Milestone 1. All five questions were run
     through `app.py retrieve` (no model calls) and each returned its correct
     source document at rank 1:

       laundry cost in Old Brewhouse     0.194  housing_old_brewhouse_laundry
       salad bar at Kestrel Commons      0.230  dining_kestrel_commons
       pass/fail deadline                0.206  admin_pass_fail_option
       which dining hall is open latest  0.429  dining_pellew_dining_hall
       shuttle frequency at weekends     0.412  transit_shuttle

     The fourth is the one to write about. Its answer is Verrill Street Grill
     (open to 1:00am), but answering it needs the closing times of all seven
     dining halls, and TOP_K is 5. Verrill was not in the top 5 at all — the
     chunk containing the answer is never retrieved. That is a concrete reason
     to expect one miss out of five. -->

Four of my five questions are single-fact lookups, and each returns its source
document at rank 1. The fifth is not: "Which dining hall is open the latest?"
can only be answered by comparing closing times across all seven dining hall
documents, and TOP_K is 5. The correct answer is Verrill Street Grill at
1:00am, and Verrill is not in the retrieved set at all — before or after I
re-chunked. So I am not setting 4 of 5 to leave myself slack on the ordinary
questions; I am setting it because I deliberately included one question my
retrieval design cannot satisfy, and I would rather have that in the set than
five questions I already know pass.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

<!-- Evidence you have for this, from Milestone 1:
       - The instruction to cite is sent twice, not once. generate.py's
         GROUNDING_INSTRUCTION says "Name the document your answer came from,
         using the filename given in each excerpt", and build_prompt repeats
         "name the file you used" at the end of every prompt.
       - Every chunk arrives labelled "[from <filename>]", so the filename is
         always in front of the model.
       - It worked first time: the housing lottery answer ended with
         "Source: admin_housing_lottery.txt".
       - What would have to go wrong: the model ignores both instructions.
         That is possible but not something the pipeline makes likely, which
         is why this one is 5 of 5 rather than 4. -->

The pipeline asks for a citation twice, not once: `GROUNDING_INSTRUCTION`
tells the model to name the document, `build_prompt` repeats it at the end of
every prompt, and every chunk arrives labelled `[from <filename>]` so the
filename is never out of sight. Both answers I have run named their sources.
With three separate things pushing in the same direction, a target of 4 of 5
would be one I could only miss by accident, so 5 of 5 is the honest number.

One thing I want to be explicit about before I measure it: a question the
relevance gate refuses produces no sources, because it never reaches the
model. I am counting only answers the gate let through. Refusals are what
criterion 3 measures, and scoring them here as well would mean one event
failing two criteria.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

<!-- Evidence you have for this, from Milestone 1. Both groups were measured
     with `app.py retrieve` at the default 0.6 cutoff:

       in corpus       0.194  0.206  0.230  0.412  0.429
       out of corpus   0.825  0.844  0.886  0.896  0.934

     The gap runs from 0.43 to 0.83 with nothing in it — about twice as wide
     as the spread within either group. All five out-of-corpus questions
     already refuse at 0.6.

     So the honest question for your sentence is the opposite of the usual
     one: with a gap that clean, is 4 of 5 too easy a target? Say what you
     think and why. Deciding it is too easy and tightening it to 5 of 5 is a
     defensible call; so is keeping 4 of 5 because the gap was measured on one
     chunking and Milestone 3 will move the distances underneath it. -->

I measured both groups, and the separation is not close. In corpus: 0.146,
0.185, 0.206, 0.421, 0.421. Out of corpus: 0.825, 0.848, 0.877, 0.886, 0.923.
The gap between the two runs from 0.42 to 0.83, roughly twice as wide as the
spread inside either group, and all five out-of-corpus questions already
refuse at the 0.6 default. On those numbers I expect 5 of 5, not 4.

I am keeping 4 of 5 anyway, and I want the reason on record rather than
discovered later: these distances are a property of one chunking, not of the
corpus. Re-chunking in Milestone 3 moved every in-corpus distance — the
shuttle question went from 0.412 to 0.182 — and anything I change in unit 2
will move them again. The one number I am least willing to bet on holding
exactly is the one I have measured exactly once.

---

## 4. Chunks read as complete thoughts

For at least 4 of 5 chunks sampled with `python app.py chunks -n 5`, the chunk
reads as a complete thought — no sentence is cut in half at either end, and the
chunk does not begin or end mid-clause.

**Why this target:**

<!-- Evidence you have for this, from Milestone 1:
       - Your 88 documents run 178–549 characters. CHUNK_SIZE is 800, so
         fallback_split never fires: 88 documents came out as 88 chunks and
         every one is currently a whole document.
       - That means you score 5 of 5 today without trying. The target is aimed
         at Milestone 3, where you replace the chunker and start splitting.
     One or two sentences: why 4 and not 5? -->

My chunker splits on paragraph breaks, so in principle a sentence can never be
cut in half and I should score 5 of 5. The reason I am not claiming 5 is the
rule that props it up: paragraphs shorter than 80 characters get merged into
the one after them. That is a length test, not a meaning test, and it can
just as easily glue two unrelated paragraphs together — producing a chunk
that is grammatically whole but covers two topics, which fails the spirit of
this criterion while passing the letter of it. The shortest chunk in my
sample, `course_cs_340_exams.txt#1` at 103 characters, is close enough to
that line that I looked at it twice. One failure in five is the room I am
leaving for that merge rule being wrong.

---

## 5. Retrieval brings back more than one useful chunk

For at least 4 of my 5 test questions, at least 2 of the 5 retrieved chunks are
relevant to the question — meaning a reader could use them to help answer it,
not merely that they came from a related topic.

**Why this target:**

<!-- Evidence you have for this, from Milestone 1:
       - "is the housing lottery random?" retrieved 5 chunks. One was right.
         The other four were admin_parking_permits, advising_registration,
         housing_morrow_house and housing_tamsin_court — all campus topics,
         none about the lottery.
       - TOP_K is 5, so four of five slots were wasted on that question.
       - Counter-pressure: your corpus is 88 single-topic documents, so for
         some questions there may genuinely only be one relevant chunk to
         find. That is why this says 4 of 5 questions, not 5 of 5.
     One or two sentences: why 2 relevant and not 1 or 3? -->

This is the criterion I care most about, because the first question I ever ran
failed it. "Is the housing lottery random?" retrieved five chunks and exactly
one was useful; the other four were parking permits, course registration, and
two dorms with nothing to do with the lottery. The answer was right, but four
of five retrieval slots did no work.

I picked 2 and not 3 because my corpus is 88 single-topic documents, and for
a narrow question there may honestly only be one or two chunks in existence
that bear on it — a target of 3 would be measuring the corpus, not my
pipeline. I picked 2 and not 1 because 1 is where I already am, and a target
I have already met is not a target. I set it at 4 of 5 questions rather than
5 because the dining hall comparison question retrieves five chunks from the
wrong halls, and I do not expect any amount of chunking to fix that.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
