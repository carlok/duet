# The evolutionary search

[← README](../README.md)

## How it works

- **The space.** Every law of order at most 4, meaning at most four operation symbols: 71,369 up to renaming, 61,983
  of them bridges. A theory is a set of 2 to 6 such laws.
- **A cheap guess at implication.** We record once which laws hold in each of 12,509 small structures on 2–6
  elements. To guess what a theory implies, take the structures that satisfy it and collect the laws true in all of
  them. It is only a guess, and every countermodel found later joins the collection.
- **MAP-Elites.** A quality-diversity algorithm sorts theories into cells by a few features. Each cell keeps its best
  theory, and new theories come from mutating and combining old ones.
- **Verification.** Every cell win goes at once to verifier processes:
  1. countermodels on up to 6 elements, and the independence of the laws;
  2. the prover E;
  3. Vampire's finite model builder;
  4. Mace4, up to 10 elements.

  A prover saturation, checked independently, settles claims that only infinite models refute. Only proved laws count.
- **Discipline.** Every scaled run is preregistered ([`PREREGISTRATION.md`](../PREREGISTRATION.md)), and deviations
  are listed there.

## What each round taught

Each round taught one lesson, and the search was changed to answer it.

1. **It rediscovers.** Against a catalogue of 13 known two-operation structures fixed in advance, it found 7.
   - Named theories have a syntactic duality and random ones do not: 8 of 10, against 0 of 120.
   - A prior that rewards dualities raises the share of fragments of a named theory from 8% to 33% (preregistered,
     p = 2 × 10⁻²⁵).

   Rediscovery is the calibration: the search finds what humans found.
2. **Its best candidates were disguises.** The top non-fragments were old structures in costume:
   - split theories, a theory of `·` beside a theory of `∘`, whose bridges only look like bridges;
   - one-operation structures with their division written as `∘`;
   - absorption-type subvarieties.

   One core came from a distant field: that of `10c98c4b` is the Δ-bijectivity of the Yang–Baxter literature.
   Filters for the first two disguises went into the verifier (run X3). After that, 0 of X3's 570 scored
   non-fragments is split, against 33 of 654 before.
3. **It had learned one trick.** 97% of all scored theories proved an emergent law in one variable, such as
   `x · x = x ∘ x`, and none proved emergent associativity. The score rewarded what a fusion forces on squares. The
   lattice reference case itself is of that kind. A new arm, *fusion* (run X4), does three things:
   - it counts only synergy off the diagonal;
   - it skips theories valid in the 2-element lattice;
   - a quarter of its proposals are a law of `·`, a law of `∘` and a bridge: two traditions and a link.

   None of its 565 scored theories is a fragment of a named theory (X3: 31.6%), and finite models refute 21% of its
   claims, against 3%. But the attractor moved instead of disappearing: `x · (x · y) = x · x` and its kin.
4. **The attractor was a derived operation that ignores an argument.** Run X5 skipped every theory that implies one,
   keeping only *rigid* theories. 0 of 164 scored theories are fragments, and the attractor is gone. But all 20 of its
   top candidates have affine models over 𝔽₄. In 16, `·` is a Steiner loop and `∘` the same loop translated by a
   constant, `x ∘ y = (x · y) · (z ∘ z)`. That is one operation plus a parameter, a disguise our checks missed. A new
   attractor appeared: `x · (x · x) = y · (x · y)`.

5. **Screening the disguise moved the search.** Run X6 added the parameter-definition screen (verifier V6). It fired on
   356 theories, and none of X6's top 20 is a translate disguise. The top candidates left the affine region: 11 of 20
   have no classical model (X5: 0), they are 17 distinct varieties (X5: 5), and 7 have every automatic mark. X6's
   candidates now hold N1 ranks 1 to 4. None has been studied closely yet. X5's attractor
   `x · (x · x) = y · (x · y)` remains.

6. **Skipping the already known (X7).** The searcher skipped every theory that is, on the corpus, a fragment or a
   subvariety of a known structure, or equivalent to an earlier candidate, and every theory an earlier run had already
   pushed. Disguises fell from 24% to 2% of verified theories, scored theories rose from 44% to 69%, and 12 of the top
   20 carry every automatic mark. Memory stopped the run after 2.65 hours.

Both filters X5 called for now exist. A definition with a parameter (verifier V6) catches 18 of X5's 20 candidates and
none from earlier runs. Ignored variables that repeat (arm `fusion3`) are implied by 151 of all 158 candidates, so
that filter would confine a run to the quasigroup-like corner. It was not used.

7. **Volume did less than direction (X8).** Eight searchers kept alive took level 0 past 100 million. They added 11
   structured families, against 118 from the much smaller fusion runs X4 to X7.
8. **A faster verifier (X9).** Verifier V7 stops running z3 once E has proved a claim, and tries linear models over finite
   rings first. It verified 88.8 theories per verifier-hour, about five times more than before, and the linear models
   refuted 17% of the claims they ran on, in about a second each.
9. **Back to the Steiner corner (X10).** Half of X10's verified theories were parameter disguises of one shape,
   `x ∘ y = x · ((z · z) · (y · (z ∘ z)))`, and 15 of its 20 candidates have models over 𝔽₄. V6 caught every disguise,
   but only in the verifier, after the search had spent its cells on them. The screen therefore moved into the search.
   Arm `fusion5` skips such a theory before it takes a cell: a corpus test, confirmed by Mace4 on 2 to 5 elements.
10. **The skip in the search (X11).** No parameter disguise reached the verifier, for 0.11% of searcher time. 48% of
    X11's verified theories are structured (X10 11%), only 5 of its 20 candidates have a classical model (X10 15), and
    two of them lead the ranking. The Steiner shape is still there without a disguise. A side finding: the searchers
    stop pushing once the verified scores rise past their gate. X11 pushed 99% of its theories in its first 14 minutes,
    and the verifiers worked on them for 8 hours.
11. **Diversity over families (prototype).** The attractors come from the score, not from a lack of random variation, so
    arm `fusion6` adds diversity pressure. The family of a theory becomes one of its cell's coordinates, and common
    families lose queue priority. Offline, the 500 theories the verifiers would reach span 162–180 families, against
    64–76. Its rescore is now throttled (tested); it needs a live test before a run.

Details, numbers and commands: [`REPORT.md`](../REPORT.md). Next: [the ranking](ranking.md).
