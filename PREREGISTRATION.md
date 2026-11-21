# Preregistration

Each section is committed before its run starts. Changes after the start are listed under "Deviations".

## T4: duality-prior search against a matched control (written 21 Nov 2026, evening, before the run)

- **Arms.** `prior`: the searcher with the duality-closure mutation and the score factor (1 + number of
  dualities). `noprior`: the same searcher without both (same filters: bridge, non-degenerate model,
  definitional theories rejected; same cap of 6 laws). Code as of the commit that adds this section.
- **Isolation.** Each arm has its own data directory (`python -m soup.t4_setup`): matrix files linked, a copy
  of the corpus store as it stands after the stage-c sweep of 21 Nov 2026 (the common start), and its own
  queue, dedup markers, gate, results, journal and corpus growth. Nothing is shared between the arms while
  they run.
- **Verifier V2** (`SOUP_VERIFIER=V2`, `soup/verify.py`), the score change decided before this run:
  - difficulty of a proved claim = E 3.2.5 `--auto` proof steps / 10 (z3 effort still recorded);
  - a claim E did not prove gets 0.1;
  - stage a verifies one claim per order level (at most 4 pending, 12 tried);
  - every E saturation gets a convergence certificate;
  - stage c starts Mace4 at the smallest size stage a left unsearched.
- **Compute.** Both arms run at the same time on the 11-core VM, each under its own supervisor: 2 searchers
  and 3 verifiers at the start. Rebalancing within an arm is allowed; the total stays 5 processes per arm.
  Budget 14,400 s (4 h) per arm. Seeds: prior 201–, noprior 301– (one per searcher started). z3-solver
  5.4.1.0, E 3.2.5, Mace4 2026-8A.
- **H1 (primary).** Among verified theories with positive score, the share that are fragments of at least
  one of the 10 named theories of T3 (`python -m soup.fragments`; a law is valid by an E or z3 proof, invalid
  by a corpus model of the named theory or a certified saturation) is higher in `prior` than in `noprior`.
  One-sided Fisher exact test, α = 0.05; undecided theories are excluded from the test, and the two bounds
  (undecided counted as fragments, as non-fragments) are reported. Pilot (first session, different verifier,
  control without the definitional filter): 64/97 against 6/59.
- **Secondary (descriptive).** The 10 highest-scoring non-fragment theories per arm, deduplicated across arms
  up to the three dualities and up to equivalence (E proves each theory's laws from the other; compared only
  when the model counts on 2–5 elements agree). None is called new without a literature check and a check
  against the Equational Theories Project data where the theory specialises to one operation.
- **Stop rule.** Each arm runs once for its budget, without extension or rerun. Crashed workers are restarted
  by the supervisor and reported. If a supervisor dies, its arm is reported as it stands; a rerun would be a
  deviation, written before it starts.
- **Known limits, reported with the result.** Only queue-top theories get verified (priority by the cheap
  score): any arm difference inherits this selection. The arms' corpora diverge as each verifies its own
  theories; that is part of each arm. E's proof length is an upper bound on proof length: proof minimisation
  shortens ETP proofs several-fold (Kondylidou, Blanchette, Heule, arXiv:2605.21200: 62 to 20 steps, 151 to
  10), so V2 difficulty ranks proofs only roughly. (Added before the run, after the literature check.)
- **Analysis.** `SOUP_DATA=/data/t4-prior python -m soup.fragments`, the same for `t4-noprior`, then
  `python -m soup.t4_report`.

## T3: calibration, named vs random theories (written 21 Nov 2026, before the run)

- **Theories.** 10 named theories of order ≤ 4 (`soup/calib.py`): lattice, skew lattice, dimonoid,
  absorption pair, left quasigroup, right quasigroup (the first session's six), plus bisemilattice,
  right absorption pair, idempotent left quasigroup, idempotent right quasigroup. (Racks and quandles do not
  fit: left self-distributivity has order 5.)
  Random theories: 30 per size k present among the named ones (k = 2, 3, 5, 6: 120 in all), k distinct
  laws uniform over the 71,368 non-trivial laws, kept if ≥ 1 bridge and a non-degenerate base-corpus model.
  Seed 11.
- **Verification.** `verify` stages a+b with E (z3-solver 5.4.1.0, E 3.2.5), on the shared corpus store.
- **H1 (primary).** Named theories have a duality more often than random ones. Test: one-sided Fisher exact
  test on the 2×2 table (named/random × duality yes/no), α = 0.05. The named theories were chosen by people,
  and several were chosen *because* they are symmetric: H1 is a sanity check of the duality prior, not a
  discovery.
- **H2 (descriptive, no test).** On gain, max difficulty (z3), max E proof steps, model richness and score,
  report each named theory's percentile among random theories of the same size. First-session expectation:
  9th–91st percentiles, i.e. these measures do not separate named from random theories.
- **Stop rule.** All 130 theories verified once; no reruns, no exclusions after the fact. A theory whose
  verification crashes is reported as such.
- **Analysis.** `python -m soup.calib_report work/calib_t3.json`.

## Deviations

1. **T3, k = 6 null (21 Nov 2026, before any calibration result existed).** Uniform rejection sampling
   accepted 0 of 267,682 draws at k = 6 (k = 5: 7 of 308,389; k = 3: 1,650 of 434,019; k = 2: 31,473 of
   549,832; 20 s each). The k = 6 random theories are instead drawn model-first: a non-degenerate base
   structure uniformly at random, then 6 distinct laws it satisfies, at least one a bridge. Same filter,
   different weighting; the 6-law comparisons (lattice, skew lattice, bisemilattice) are reported as against
   this null. k = 2, 3, 5 stay uniform. Fisher's test is reported on all random theories and on the uniform
   ones only.
2. **T3, crashed run resumed (21 Nov 2026, evening, after 69 of 130 results existed).** The run stopped
   at 69 results: the kernel of the Podman VM OOM-killed one worker (python, 5.9 GB resident, 12:56 VM time),
   and the broken process pool ended the whole run. Which theories were in flight is not known; none of them
   has a result. The 69 results were looked at before this deviation was written (duality counts: named 8/10,
   random 0/59); nothing below depends on them.
   - Fix: every theory runs in its own child process. z3 is capped at 1.5 GB (as in the stream verifier);
     E and Vampire are capped at 2 GB. A child that dies, or runs longer than 1 h, is recorded as `crashed`.
     6 theories at a time instead of 10.
   - The 61 theories without a result (1 at k = 2, 5 at k = 3, 25 at k = 5, 30 at k = 6) are verified once
     with the same verifier settings (`verify.V1`). The 69 results are kept and not rerun.
   - A theory that crashes is reported as crashed. It counts for H1, since having a duality is syntactic,
     and is left out of the H2 percentiles.
   - Caveats: the 69 ran without memory caps, which can only turn a run that would have used more memory
     into an unknown; the shared corpus has grown since the start (stream runs), so later theories see more
     structures. Both are reported with the results.
