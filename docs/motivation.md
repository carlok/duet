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

Background from scratch, in 9 pages: [`intro/intro-reading.pdf`](../intro/intro-reading.pdf).

Next: [the evolutionary search](search.md).
