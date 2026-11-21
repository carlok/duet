# Preregistration

Each section is committed before its run starts. Changes after the start are listed under "Deviations".

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
