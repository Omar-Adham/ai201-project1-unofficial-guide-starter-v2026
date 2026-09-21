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

<!-- Your sentence goes here. -->

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

<!-- Your sentence goes here. -->

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

<!-- Your sentence goes here. -->

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
