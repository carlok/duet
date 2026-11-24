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

**The caveat.** The space is large and the human literature is larger. All runs together have verified 7,476
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
| X6 (screen for disguises) | 0% | 33% | 0% |
| X7 (skip the known) | 0% | 27% | 0% |

A higher refutation rate means the corpus's guesses get worse, which is what happens on less charted ground. Sources:
`REPORT.md`, sections T4, X2, X3, X4, X5, X6 and X7. "Disconnected" candidates, the ones with every automatic mark,
went from 0 of 20 in X5 to 7 in X6 and 12 in X7.

The image has two limits:
- **What is measured is the distance from our own checks and catalogue, not from human mathematics.** X5 looked
  unexplored to every automatic check. Its top candidates then turned out to be Steiner loops in disguise, a
  19th-century structure. The coral can grow into water that we have not charted and humans have.
- **Growth is not yet progress toward something new.** So far, each new branch came from naming the attractor that
  the previous one fell into.

**Milestones, and what the families say about them.** The author's framing for level 0:
- 50M, the dust removed: passed;
- 100M, the surface scratched;
- 200M, digging, where very unexpected things start to emerge.

The families statistic ([`families.md`](families.md)) puts a number on the hope that new kinds of structure appear
as the search grows.
- **So far, direction mattered more than volume.** The prior-arm runs (root to X3) made 51M of the 63.7M cheap
  evaluations and found 6 structured families. The fusion arms (X4–X7) made 12.5M and found 118.
- **For the milestones,** this means 100M and 200M will mean "digging" only if the extra volume goes to new
  directions. That is why X8 keeps the arm that skips the known.

So the claim is that the search grows outward from known mathematics and leaves the corner our checks recognise. It is
not that the search reaches unexplored mathematics. That needs a specialist.

## Where this sits: taxonomy first, then patterns, conjectures and theorems

The work so far is taxonomy: the search finds new "species", and F1 classifies them. The plan is to catalogue
patterns across families next, then state conjectures, and perhaps prove theorems. A literature check
([`notes/metafield.md`](../notes/metafield.md)) shows that this arc is not a new field. The ground is held by:
- **automated theory formation:** AM in 1976, then HR, which ran our prover and model-finder loop on finite algebras;
- **Wolfram's ruliology:** he enumerates axiom systems and calls the activity a new science that starts like natural
  history;
- **catalogues of one-operation varieties:** Le Floch's 456 semigroup varieties, SemiBase, and the ETP's lattice of
  order-3 conjunctions;
- **the catalogue-to-theorem arc:** the BSD conjecture, Graffiti, and the murmurations of elliptic curves.

What the check did not find is our combination. That is an open-ended search over *sets* of laws in *two*
operations, with synergy as the target, a taxonomy of the theories it finds, and conjectures stated across those
families. That combination is the claim.

Background from scratch, in 10 pages: [`intro/intro.pdf`](../intro/intro.pdf); exercises in [`intro/exercises.pdf`](../intro/exercises.pdf).

Next: [the evolutionary search](search.md).
