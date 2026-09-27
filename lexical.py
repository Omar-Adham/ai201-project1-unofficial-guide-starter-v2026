"""
The lexical half of hybrid retrieval — unit 2, Milestone 4.

Added to fix one diagnosed failure: the relevance gate could not tell a
question my corpus covers from one it doesn't, because embedding distance
measures how a question is *phrased*, not whether the answer is there.

    What are the gym opening hours?    0.496  — no gym document exists
    Is there a campus health centre?   0.527  — health_center.txt exists

Those are in the wrong order, so no value of THRESHOLD separates them. The
missing evidence is lexical: "gym" appears in 0 of 159 chunks. Embeddings
cannot represent absence, because every vector is close to something.

**Why this is IDF-weighted coverage rather than BM25**, when `rank-bm25` is
already in requirements.txt and I tried it first.

BM25 scores are unbounded and only meaningful *relative to other chunks for
the same query*. To blend one onto a distance scale that a fixed cutoff
reads, you have to normalise it, and normalising per query is exactly what
breaks the thing I am trying to fix: it hands the best chunk a perfect score
whether it is a real match or the least-bad of 159 irrelevant ones. The gym
question would come out looking like a direct hit.

So the lexical signal here is *absolute*: of the information in this
question, measured as IDF, how much of it actually appears in this chunk? A
query term in no chunk at all gets the maximum IDF and can never be matched,
so it holds the score down permanently. That is the signal the gate needs,
and it is the one BM25 throws away.
"""

import math
import re

import config

# Split on anything that isn't a letter or digit. Deliberately crude: it keeps
# "1:00am" as "1" and "00am", and "pass/fail" as "pass" and "fail", which is
# what I want — a question asking about pass/fail should match a document
# saying "pass/fail" on both halves.
_TOKEN = re.compile(r"[a-z0-9]+")

# Words carrying no information about which document answers a question. This
# matters more than usual here: every question in this corpus is a short
# natural-language sentence, so without this the grammar drowns out the two or
# three words that actually pick a document.
_STOPWORDS = frozenset(
    """
    the a an is are was were do does did i how what when where which who why
    can could should would will to of in on at for it there their my me much
    many and or if that this with from by as be been have has had you your
    get go going am long far any some about into over
    """.split()
)

# semantic weight. 0 = keyword search only, 1 = the old behaviour exactly.
# Left at the midpoint on purpose: tuning it would be a second change, and I
# have no held-out questions to tune it against. See the README.
ALPHA = 0.5

_stats: dict[str, tuple[int, dict[str, int]]] = {}


def tokenize(text: str) -> list[str]:
    """Lowercase words, stopwords dropped."""
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


def corpus_stats(corpus: str | None = None) -> tuple[int, dict[str, int]]:
    """How many chunks there are, and how many contain each term.

    Computed from the documents rather than read back out of Chroma, and
    memoised per corpus. It costs one pass over 88 short files and no
    embedding, so it is far cheaper than the vector search it rides along
    with.
    """
    corpus = corpus or config.CORPUS
    if corpus in _stats:
        return _stats[corpus]

    from chunker import split_documents
    from ingest import load_documents

    chunks = split_documents(load_documents(corpus))
    document_frequency: dict[str, int] = {}
    for chunk in chunks:
        for term in set(tokenize(chunk.text)):
            document_frequency[term] = document_frequency.get(term, 0) + 1

    _stats[corpus] = (len(chunks), document_frequency)
    return _stats[corpus]


def idf(term: str, total: int, document_frequency: dict[str, int]) -> float:
    """Inverse document frequency, with unseen terms at the ceiling.

    A term in no chunk gets df 0 and therefore the largest value this can
    return. That is the point: "gym" is the most informative word in "what are
    the gym opening hours", and the informative thing it tells us is that this
    corpus cannot answer the question.
    """
    return math.log((total + 1) / (document_frequency.get(term, 0) + 1))


def coverage(question: str, text: str, corpus: str | None = None) -> float:
    """Fraction of the question's information, by IDF, present in this chunk.

    1.0 means every meaningful word in the question appears here. 0.0 means
    none of them do. Absolute — it does not depend on how the other chunks
    scored, which is what makes it usable by a fixed threshold.
    """
    terms = tokenize(question)
    if not terms:
        return 0.0

    total_chunks, document_frequency = corpus_stats(corpus)
    present = set(tokenize(text))

    wanted = sum(idf(t, total_chunks, document_frequency) for t in terms)
    if wanted == 0:
        return 0.0
    found = sum(
        idf(t, total_chunks, document_frequency) for t in terms if t in present
    )
    return found / wanted


def combine(semantic_distance: float, question: str, text: str,
            corpus: str | None = None) -> float:
    """Blend semantic distance with lexical coverage, on the distance scale.

    Lower is better, same as before, and still roughly 0 to 1 — so THRESHOLD
    keeps meaning what it meant. That is not luck: coverage is a fraction, so
    `1 - coverage` is a distance-shaped number, and a weighted average of two
    such numbers stays in range.
    """
    lexical_distance = 1.0 - coverage(question, text, corpus)
    return ALPHA * semantic_distance + (1.0 - ALPHA) * lexical_distance
