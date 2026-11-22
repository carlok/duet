# Preregistration

Each section is committed before its run starts. Changes after the start are listed under "Deviations".

## X2: a second exploratory run, as X1 (written 22 Nov 2026, 04:25 UTC, before X2 starts)

Exploratory and descriptive only: no hypothesis is tested. The user asked that, with time left, a fresh batch of
candidates go through the pipeline again. X1 was cut to 1.5 h (deviation 4).

- Setup: `python -m soup.t4_setup --dir x2`, with its own `SOUP_DATA=/data/x2`. Matrix files are linked; the corpus
  is copied from the main `work/corpus` at setup.
- Search and verifier: exactly as X1. Arm `prior`, 4 searchers and 4 verifiers, verifier V3, seeds 501+. No code
  change to the search or the verifier.
- Budget: 10,200 s from the start (until about 07:20 UTC).
- Stop rule: as X1. The budget runs out, or the VM's available memory drops below 1 GB, which gets reported.
  Nothing else heavy runs next to it: no scans, no profiles, no prover batches. Light reads and docs only.
- After the run, in this order:
  1. the fragment check;
  2. the top 20 non-fragments by score join the candidate list (sources `t4-prior,t4-noprior,.,x1,x2`);
  3. profile, `soup.hidden`, `soup.split` and `soup.relabel` on the new candidates;
  4. the T5a ranking of all candidates, dossiers and Lean certificates for new entries in the top 10;
  5. a split scan of all X2 non-fragments (`soup.split --fragments 1 --jobs 4`), run last.
- Reported descriptively:
  - theories verified;
  - fragment share;
  - claims refuted by FMB;
  - split share among non-fragments;
  - the top 20 non-fragments and where they land in the ranking.
- Caveats: the corpus at the start includes neither X1's models nor X1's corpus. Not compared with X1 or T4 by a
  test.

## X1: exploratory run with verifier V3 (written 21 Nov 2026, night, during T4, before X1 starts)

Exploratory and descriptive only: no hypothesis is tested, and nothing from X1 enters T4's analysis.

- Purpose: more verified theories, from the duality-prior search, for the T5a ranking and the dossiers. The user
  asked to use the rest of the night this way.
- Setup: `python -m soup.t4_setup --dir x1`, i.e. its own `SOUP_DATA=/data/x1`. Matrix files are linked, and the
  corpus is copied from the main `work/corpus` at the time of setup.
- Verifier V3 (`soup/verify.py`): V2 plus Vampire finite model building. Stage b runs it for 60 s on every pending
  claim that E's small run neither proves nor saturates, starting from the smallest size stage a left unsearched,
  or 7. Stage c runs it for 600 s before Mace4. A model counts only after `check_offline.check_finite`.
- Search: arm `prior` (the duality closure and score factor as in T4), 4 searchers and 4 verifiers, seeds 401+.
- Budget: from the start until 07:30 UTC, at most 14,400 s. It starts after the T4 analysis, the T5a profile run
  and the T4 profiles.
- Stop rule: the budget runs out. The run is stopped early only if the VM's free memory drops below 1 GB; that would
  be reported.
- Reported descriptively:
  - verified theories;
  - the share that are fragments (`fragments.py`), without comparison to T4;
  - claims refuted by FMB that stage a missed;
  - the top 20 non-fragments by score.

  The top 20 then go through the profile and the T5a ranking, with the others in its candidate list.
- Caveats:
  - The corpus of X1 starts larger than T4's: it includes tonight's S10 model and the sweep's models.
  - Score and selection are as in T4. V3 refutes more claims than V2, so V3 scores are not comparable with T4
    scores.

## T5a: does an algebraist's profile separate named from random theories? (written 21 Nov 2026, night, before the run)

Why: the synergy score does not prefer named theories (T3, H2), so it cannot pick out theories a universal
algebraist would find interesting. Before candidates are ranked by structural features, those features are tested
on the same calibration set.

Theories: the 130 of T3 (`work/calib_t3.json`): 10 named, 120 random, including the 2 whose T3 verification
crashed. The profile needs only the laws.

Profile: `python -m soup.profile --set t3 --jobs 8` (code at the commit of this section), one child process per
theory, 1,800 s limit. Budgets:
- Mace4 enumerates all models of sizes 2–4 (60 s each) and size 5 (120 s), capped at 3,000 models per size.
- Models are counted up to isomorphism.
- Term functions: up to 60 models of sizes 2–4 for ternary terms (size ≤ 5); up to 120 models of sizes 2–5 for
  binary terms (size ≤ 7); 60 s and 20,000 functions per arity.
- E proves each identity of a candidate term in 30 s and 500,000 processed clauses, for at most 3 candidates per
  kind.

Features, all binary:
- **F1 `malcev_term` (primary):** some term of size ≤ 5 is a majority, Mal'cev, Pixley or minority term, and E
  proves every identity of that kind from the axioms.
- **F2 `finite_free2`:** the binary term functions on the models close under both operations. This is a finite
  free algebra on 2 generators of the variety generated by those models.
- **F3 `convergent`:** an E saturation against x = y passes the `soup.confluence` checks, i.e. a convergent
  presentation of a non-trivial theory.
- **F4 `spectrum3`:** non-degenerate models on at least 3 of the sizes 2–5.

Hypotheses and tests:
- H1: named theories have F1 more often than random ones. One-sided Fisher exact test.
- H2–H4: the same for F2, F3 and F4. One-sided Fisher, Holm-corrected over the three.
- A crashed profile is reported and left out of the test for each feature it lacks.

Use in ranking (fixed now, before any T4 or exploratory-run theory is profiled). Candidates are:
- the 20 best non-fragment theories by V2 score from each T4 arm;
- T1 and T2;
- the 20 best non-fragment theories of the earlier runs;
- the 20 best of the exploratory run, if it runs.

The ranking:
1. Exclude fragments of a named theory (`fragments.py`: valid) and theories that E proves equivalent, both ways,
   to a variety on the standard list (semilattices, bands, rectangular bands, left- and right-zero bands,
   lattices, distributive lattices, quasigroups), on either assignment of the two operations.
2. Rank by the number of features with p < 0.05 after Holm that the theory has. Ties are broken by duality, then
   by the number of sizes with non-degenerate models, then by V2 score.
3. If no feature reaches p < 0.05, nothing is ranked. Candidates are listed with their features, and the profile is
   reported as not calibrated.

Every listed theory is a candidate, not a result (rule 4), until a literature check and the equivalence checks are
done.

Seen before this section: the profile code was debugged on 3 of the 10 named theories, without the random ones:
- lattice: F1 (a majority term of size 4, proved), F2 (4 functions), F4;
- absorption pair: F3, F4;
- left quasigroup: F3.

No random theory and no T4 theory had been profiled.

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

3. **T5a, provers killed by the VM's OOM killer (22 Nov 2026, ~01:50 UTC, after the T5a result was seen).**
   - What happened: the T5a profile ran with 8 jobs, alongside the candidate profile (3 jobs) and `t4_report`,
     which ran 10 E processes at once. The kernel log of the Podman VM shows 10 OOM kills between 01:28 and
     01:41 UTC:
     - `soup-t5a`: 3 profile children, reported as crashed, plus 3 E runs;
     - `t4_report`: 3 E runs;
     - the candidate profile: 1 E run.
   - Why it matters: the profile recorded a killed E run as "not proved" or "did not saturate", which is a
     feature value of 0, not a crash. Which theories were affected cannot be told from the output. The
     analysis as run reported F3 (`convergent`) as calibrated (named 6/10, random 13/117, Holm p = 0.0022) and
     F1, F2, F4 as not calibrated. 3 random theories crashed.
   - Fix (commit after this entry): a prover or Mace4 killed by a signal now gives the value *unknown* for the
     feature it feeds. Per the T5a rule for crashed profiles, an unknown value leaves that theory out of that
     feature's test. `t4_report` takes its pool size from `T4R_JOBS` and reports equivalence checks whose E run
     crashed as unknown.
   - Reruns:
     - all 130 T5a theories, with the fixed code and 4 jobs, nothing else heavy running, into
       `check/profile_t3_rerun.json` (`python -m soup.profile --set t3 --name t3_rerun --jobs 4`), analysed with
       `python -m soup.profile --t5a t3_rerun`;
     - the 62 candidates, from scratch with the fixed code (the partial run is kept as
       `check/profile_candidates_asrun.json`);
     - `t4_report` with `T4R_JOBS=3`. Its primary outcome does not use E, so it cannot change.
   - Reported: both T5a analyses, as run and rerun. Fixed now, before the rerun: the ranking uses only the
     features calibrated in **both** (`soup.dossier rank`).
   - The OOM killer also hit T4 once (searcher s302 of noprior, 00:00 UTC). The supervisor restarted it, as
     preregistered; REPORT lists it with the T4 crashes.
4. **X1, stopped by its memory rule (22 Nov 2026, 03:50 UTC, before any X1 result was analysed).** X1 started at
   02:20:41 UTC with a 14,400 s budget. At 03:50:29 UTC the watcher read 170 MB of available memory in the VM, below
   the preregistered 1 GB, and stopped the run (`podman stop -t 30`; the supervisor's last journal line is
   "stopped by signal" at 03:50:43, the container exit code 137). It ran 1 h 30 min of the planned 4 h.
   - Most likely cause: I started two post hoc split scans (`soup.split --fragments`, 1 job each, each loading the
     corpus) about two minutes earlier, alongside X1's 8 workers. Twenty minutes later the VM had 9.2 GB available
     and the kernel log showed no OOM kill in the last 30 min.
   - Not restarted: the stop rule says stop, and a second start would be a run with a different budget and corpus.
   - Reported: X1 as run (1.5 h), with the descriptive outcomes listed above. The top 20 non-fragments go through
     the profile and ranking as planned.
