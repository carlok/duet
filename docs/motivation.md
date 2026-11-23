# Why: synergy, and the jazz aim

[← README](../README.md)

Take a lattice, such as `max` and `min` on numbers. Two *absorption laws* tie the operations together:
`x · (x ∘ y) = x` and `x ∘ (x · y) = x`. Neither law alone says anything about `x · x`, yet together they force
`x · x = x`. The whole implies something no part does: that is **synergy**.

Laws that mix both operations are **bridges**. Bridges are where two theories fuse into one structure:
- absorption fuses two semilattices into a lattice;
- distributivity fuses addition and multiplication into a ring;
- a rack ties an operation to its inverse.

**The aim** is the kind of jump jazz made: two traditions fused by a bridge into something that works on its own
terms but is not clearly connected to either parent. duet asks whether an open-ended search can find such fusions,
and in particular ones nobody has named yet. No language model takes part in the search or its scoring.

**The caveat.** The space is large and the human literature is larger. All runs together have verified 5,279
theories, against about 1.8 × 10²⁶ possible law sets, and most of them sit in the corner humans know best. "No source
found" by our web searches is therefore weak evidence, and finding nothing new would not be a negative result.

**Growing like a coral.** The share explored is close to zero, but the search does not sample at random. It grows
outward from known mathematics, run by run, and each run starts from the lesson of the one before. The runs move
measurably away from the corner our checks recognise:

| Run | Fragments of a named theory | Claims refuted by a finite model | Top 20 identified by the automatic checks |
| --- | ---: | ---: | ---: |
| T4 (duality prior) | 33% | | |
| X2 | | | 50% |
| X3 (disguise filters) | 31.6% | 3% | 26% |
| X4 (fusion arm) | 0% | 21% | 0% |
| X5 (rigid theories) | 0% | 24% | 0% |

A higher refutation rate means the corpus's guesses get worse, which is what happens on less charted ground. Sources:
`REPORT.md`, sections T4, X2, X3, X4 and X5.

The image has two limits:
- **What is measured is the distance from our own checks and catalogue, not from human mathematics.** X5 looked
  unexplored to every automatic check. Its top candidates then turned out to be Steiner loops in disguise, a
  19th-century structure. The coral can grow into water that we have not charted and humans have.
- **Growth is not yet progress toward something new.** So far, each new branch came from naming the attractor that
  the previous one fell into.

So the claim is that the search grows outward from known mathematics and leaves the corner our checks recognise. It is
not that the search reaches unexplored mathematics. That needs a specialist.

Background from scratch, in 9 pages: [`intro/intro-reading.pdf`](../intro/intro-reading.pdf).

Next: [the evolutionary search](search.md).
