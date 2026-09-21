"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


MIN_CHUNK = 80   # characters. Below this a paragraph is a fragment, not a thought.


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split on paragraphs, and repeat the document's title on every chunk.

    Written for `campus_life` in Milestone 3, from two things I measured about
    those documents rather than from a generic character count.

    **One: the starter never split anything.** The documents run 178 to 549
    characters and CHUNK_SIZE was 800, so 88 documents came out as 88 chunks.
    But most of those documents hold more than one thought. Kestrel Commons
    has one paragraph about wait times and the stir-fry station, and a second
    about opening hours and price. A question about hours has to match against
    the wait-time sentences too, and those dilute it. Splitting on the blank
    line separates them.

    **Two: the title is always alone on the first line.** All 88 of them.
    That matters twice over:

      - Split on blank lines naively and every document donates a 22-character
        orphan chunk that says "On the housing lottery" and nothing else.
      - Worse, the *body* paragraphs often don't name their own subject.
        "Hours are 7:00am to 9:00pm weekdays" appears without the words
        "Kestrel Commons" anywhere in it. This corpus has seven dining halls
        and seven laundry rooms written to the same template, two of which
        share whole sentences verbatim, so a chunk that doesn't name its
        building is a chunk that will be retrieved for the wrong one.

    So the title is not a chunk. It is a prefix carried onto every chunk cut
    out of that document, which is what makes each one able to stand alone.

    That prefix is also why CHUNK_OVERLAP is 0. Overlap exists so a thought cut
    in half survives in one of the two pieces; splitting on paragraph breaks
    means nothing gets cut in half, and the context a reader actually needs
    here is "which building is this about", which the title carries directly.

    CHUNK_SIZE survives as a ceiling rather than a target: any paragraph longer
    than it falls back to `fallback_split`. Nothing in `campus_life` reaches
    it — the longest body paragraph is 373 characters — but a corpus with one
    runaway paragraph shouldn't produce one runaway chunk.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        title, _, body = doc.text.partition("\n")
        title = title.strip()

        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [title]      # a document that is only a title line

        index = 0   # counts chunks within this document, not paragraphs, so
                    # that a paragraph which falls back to several windows
                    # doesn't hand out an index a later paragraph reuses

        for piece in _merge_short(paragraphs):
            text = piece if piece.startswith(title) else f"{title}\n\n{piece}"

            if len(text) > config.CHUNK_SIZE:
                # Too long to be one thought. Fall back to fixed windows for
                # this piece only, and keep the title on each of them.
                pieces = [
                    f"{title}\n\n{part.text}"
                    for part in fallback_split(
                        [Document(source=doc.source, text=piece)]
                    )
                ]
            else:
                pieces = [text]

            for body in pieces:
                chunks.append(
                    Chunk(
                        text=body,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def _merge_short(paragraphs: list[str]) -> list[str]:
    """
    Roll paragraphs shorter than MIN_CHUNK into the one after them.

    A two-line aside on its own is a fragment — it matches a question by
    keyword and then has nothing to answer it with. Joining it to the next
    paragraph costs a little focus and buys a chunk that can stand up.
    """
    merged: list[str] = []
    buffer = ""

    for paragraph in paragraphs:
        buffer = f"{buffer}\n\n{paragraph}" if buffer else paragraph
        if len(buffer) >= MIN_CHUNK:
            merged.append(buffer)
            buffer = ""

    if buffer:                          # trailing scrap, too short to stand
        if merged:
            merged[-1] = f"{merged[-1]}\n\n{buffer}"
        else:
            merged.append(buffer)

    return merged


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
