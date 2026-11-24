# REPORT

Newest first. Every number has the command that produced it. Times in the journal are UTC.

## Memory: what ended X6 and X7 early, and the fix (24 Nov 2026, recorded 05:12 UTC)

Both runs hit the memory rule early: X6 at 5.8 of 8 h, X7 at 2.65 of 8 h. The suspected cause was each process's own
copy of the growing corpus. The workers' heartbeats (`logs/stats.jsonl`, field `mem`) say otherwise:
- **Searchers** stay flat: about 300 → 380 MB PSS each over a run, corpus copy included.
- **Verifiers** grow: their private memory went from about 250 MB to 750–1,450 MB each, in X6 and in X7.
- **Prover child processes** (E, Vampire, Mace4; each capped at 2,000 MB) are not in these figures. They account for
  the rest of the gap between the workers' 7.3 GB PSS and the X6 container's 11 GB.

**Fix: verifier recycling** (`soup/stream/verifier.py`, `soup/stream/supervisor.py`).
- With `--recycle-mb N` (passed on as `SOUP_VERIFIER_RECYCLE_MB`), a verifier checks its private memory after each
  finished task. Above N it exits with code 75.
- The supervisor logs "recycled (memory)" and starts a fresh verifier with the same preference.
- Tasks are never interrupted, because the check runs only between them.
- The default is off, so earlier runs are unchanged.

**Smoke test** (5 min, arm `fusion4`, `--recycle-mb 350`, deleted afterwards): one verifier recycled at 354 MB, a
fresh one took over, no claimed task was left, and 29 theories were verified. One verifier log shows a traceback at
shutdown: the end-of-budget SIGTERM interrupted a z3 call. Its task had been released, so this is harmless. 80 tests
pass.

**For the next long run:** `--recycle-mb 700` (a fresh verifier sits near 300 MB) together with `--mem-stop-mb 1000`
as the safety net.

## X7: skip what is already known (23 Nov 2026, 19:47–22:27 UTC; preregistered; stopped by its memory rule)

Preregistration: PREREGISTRATION.md, X7 (commit `f67296f`, before the start). Arm `fusion4` = X6's `fusion2` plus three
changes:
- a known-library skip (`soup/known.py`);
- a seen-before skip;
- a distinct level-0 bitmap.

The verifier is V6, as in X6. The supervisor applied the memory rule by itself (`--mem-stop-mb 1000`): 963 MB were
available after 9,539 s (33% of the 8-hour budget), and it stopped the run cleanly. This is the preregistered rule,
not a deviation.

Commands:
- run: as in the preregistration;
- post-run: `work/check/x7_post.log` (fragments, statistics, candidates, profile, hidden and `--param`, relabel, rank,
  rediscover), split per candidate (`notes/split_x7_candidates.out`, merged into `check/split_candidates.json`),
  `notes/disconnected.py x7 x6`, `soup.dedupe`, and `notes/x7_predictions.py` (output `notes/x7_predictions.out`).

| | X7 (fusion4, V6; 2.65 h) | X6 (fusion2, V6; 5.8 h) |
| --- | --- | --- |
| verified theories | 737 (278 per hour) | 1,460 (253 per hour) |
| positive score | 511 (69%) | 645 (44%) |
| fragments of a named theory | **0 of 511** | 0 of 645 |
| screened: parameter definition / split / division | **16** / 60 / 0 | 356 / 75 / 2 |
| skipped in the searcher: known / earlier candidate / seen before | 237,413 / 4,932 / 1,395 | – |
| skipped: lattice-valid / argument-ignoring | 107,502 / 91,112 | 145,478 / 147,658 |
| claims / proved | 1,369 / 877 | 1,756 / 868 |
| refuted by finite models (stages a and c, and FMB) | 370 (27%) | 572 (33%) |
| refuted by E saturation | 47 (33 uncertified) | 118 (58 uncertified) |
| unknown / open | 68 / 7 | 184 / 14 |
| structures added to the corpus | 6,703 | 8,055 |
| cheap evaluations (stats / searcher heartbeats) | 2,188,667 / 2,403,574 | 4,004,695 / 4,228,908 |
| distinct evaluations (union of the bitmaps) | 1,772,881 (73.8% of heartbeats) | not measured |

**Predictions:**
- **Q1 holds.** Among X7's top 20, `soup.relabel` and `soup.rediscover` find no fragment, subvariety or equivalent of
  a named or catalogue theory: R1 had no theory to check, 0 E jobs. `soup.dedupe` finds none equivalent to an earlier
  candidate.
- **Q2 fails.** 73.8% of evaluations are distinct, against the predicted ≥ 80%. A quarter of the cheap evaluations
  still repeat a law set.
- **Q3 holds.** The top 20 are 19 varieties, and **12 of 20 are "disconnected"** (X6 7, X5 0, X4 14).
- **Q4 holds.** The parameter screen fired on 2.2% of verified theories (X6 24%).

**Other checks:**
- Split: 20 of 20 not split (finite certificate).
- Hidden, with and without a parameter: 0.
- 13 of the top 20 have no classical model.
- Over all runs, 198 candidates are 161 varieties.
- In N1, X7's `de0c0cf3` enters at rank 2; it has not been studied.
- Funnel: 59.5 M evaluations, 7,476 verified, 106 not known, 36 at level 7.

**Reading:**
- **Skipping the known moved the verifier's time to new ground.** Disguises went from 24% to 2%, scored theories from
  44% to 69%, and disconnected candidates from 7 to 12.
- **The attractor x·(x·x) = y·(x·y) and its variants still top the proved laws.**
- **The memory rule ended both X6 and X7 early.** Every searcher and verifier holds its own copy of the corpus, which
  grew by 6,703 structures here. A night-long run needs a memory fix: one shared corpus, or a cap on what each
  searcher loads.

## X6's N1 ranks 1–4: close looks (23 Nov 2026, recorded 14:29 UTC; post hoc)

Commands: `notes/dig_light.py <key>` and `notes/x6_top4_checks.py` parts 1–2 (E, 20–60 s per goal). Memo:
`notes/x6_top4.md`. Literature: one web-only agent; its ETP numbers were checked by `law_index`.

| Check | family `bc43fd42`, `d0e963d9`, `d14ced44` | `3818b88f` |
| --- | --- | --- |
| structure | each implies the core K = {x·(y·y) = x, x·(y∘y) = x, x·(y·z) = x·(z∘y)}; K implies none; no implications between them (E, 60 s) | equivalent to: · commutative with x·(x·y) = y (a totally symmetric quasigroup), x∘x = x, (x·x)∘x = x, x∘(x·y) = x∘y (E both ways) |
| reading | squares are right identities for ·; left multiplication cannot tell y·z from z∘y | a triple system with a selector: x∘y depends only on x and the block {x, y, x·y} |
| shadow (· = ∘) | left-zero band | one-element models only |
| ETP | x = x◇(y◇y) is 11; x◇(y◇z) = x◇(z◇y) is 4358; neither named | Equations 16, 26 and 43 (commutativity) |
| literature | x(yz) ≈ x(zy) only in one-operation AC-spectra work (arXiv:2401.15786) | TS-quasigroups, squags and sloops, cubic curves; nothing with a second operation like ∘ |

**Models of `3818b88f`** (`notes/3818b88f_models.py`, labelled tables, output `notes/3818b88f_models.out`). Every
TS-quasigroup on n ≤ 4 elements carries ∘ operations satisfying the reading: 2, 29 and 1,024 of them for n = 2, 3, 4,
of which 2, 28 and 432 are selectors (x∘y in {x, y, x·y}). On 4 elements every choice of one value per (point, block)
works, so ∘ is nearly free. Sampled models pass the five original laws.

**Verdict:** none identified. Funnel level 8 now holds 8: the four above plus `55cb2c91`, `1d0a5211`, `742cc445` and
`97a7dfcf`. The funnel also counts a memo whose title names several candidates (`soup/funnel.py`).

## X6: X5 with the parameter-definition screen (23 Nov 2026, 06:40–12:26 UTC; preregistered; stopped by its memory rule)

Preregistration: PREREGISTRATION.md, X6 (commit `cc1dc25`, before the start). Single change from X5: verifier V6
(parameter-definition screen). It stopped at 72% of its 8-hour budget by the memory rule (deviation 9). Commands:
- run: `podman run -d --name soup-x6 -v "$PWD/work:/data" -e SOUP_DATA=/data/x6 -e SOUP_VERIFIER=V6 soup python3 -m
  soup.stream.supervisor --arm fusion2 --searchers 4 --verifiers 4 --seed0 1001 --budget 28800 --run x6`;
- post-run pipeline: fragments, statistics (`notes/*_x6.out`), candidates (`--sources ...,x5,x6`), profile,
  `soup.hidden` (plain and `--param`), `soup.relabel`, rank, `soup.rediscover --sources x6`; log
  `work/check/x6_post.log`;
- split per candidate (`notes/split_x6_candidates.out`), `notes/disconnected.py x6 x5`, `soup.dedupe --jobs 4`.

| | X6 (fusion2, V6; 5.8 h) | X5 (fusion2, V5; 2.5 h) |
| --- | --- | --- |
| verified theories | 1,460 (253 per hour) | 292 (117 per hour) |
| positive score | 645 | 164 |
| fragments of a named theory | **0 of 645** | 0 of 164 |
| screened: parameter definition / split / division | **356** / 75 / 2 | – / 13 / 0 |
| skipped: lattice-valid / argument-ignoring | 145,478 / 147,658 of 4,228,908 searcher evaluations (3.4% / 3.5%) | 2.9% / 3.1% |
| claims / proved | 1,756 / 868 | 477 / 274 |
| refuted by finite models (stages a and c, and FMB) | 572 (33% of claims) | 114 (24%) |
| refuted by Vampire FMB | 143 (sizes 5–12; FMB ran on 341 claims) | 79 |
| refuted by E saturation | 118 (58 uncertified) | 9 (8 uncertified) |
| unknown / open | 184 / 14 | 76 / 4 |
| emergent associativity / commutativity proved | 0 / 53 | 0 / 92 |
| structures added to the corpus | 8,055 | 437 |
| cheap evaluations (stats) | 4,004,695 | 2,384,983 |

**Predictions:**
- **Q1 holds.** `soup.hidden --param` catches 0 of X6's top 20.
- **Q2 holds.** X6's 20 are 17 varieties (`soup.dedupe`; X5: 5). Over all runs, 178 candidates are 142 varieties.
- **Q3 holds.** x·(x·x) = y·(x·y) is again the most frequent proved emergent law (121 of 645).
- **Q4 fails, in the good direction.** 9 of the top 20 have a classical model, against the predicted ≥ 15 (X5: 20 of
  20).

**Post-run checks:**
- **Candidates:** 178 in the pool.
- **Hidden and relabel:** 0 definitional, 0 relations to a named theory.
- **Split:** 0 split, 9 not split (finite certificate), 10 undecided, 1 timed out. The per-candidate results of X5
  and X6 were merged into `work/check/split_candidates.json`, where the other checks read them.
- **R1:** 2,018 E jobs, 1,328 unknown, a high share that weakens the automatic identification.
  - No theory is a fragment of, or equivalent to, a catalogue entry.
  - Subvarieties: 54 of doppelsemigroups, 5 each of left and right quasigroups, and 1 of Δ-bijective pairs.
  - The top 20: 0 identified automatically.
- **"Disconnected" marks** (`notes/disconnected_x6_x5.out`): **X6 7 of 20**, X5 0 of 20, X4 14 of 20. The seven are
  `e1d5daf1`, `6f1f0350`, `3818b88f`, `d14ced44`, `a35cf10e`, `bc43fd42` and `d0e963d9`.

**Reading:**
- **The screen worked during the run.** It fired on 356 theories (24%), and none of the top 20 is a translate
  disguise.
- **The search moved.** After the screen took the Steiner-loop translates away, the top candidates left the affine
  region: 11 of 20 have no classical model, against 0 of 20 in X5. Seven have every automatic mark. They are
  candidates for close looks, not results.
- **The old attractor stays.** `fusion2` does not filter x·(x·x) = y·(x·y).
- **Caveat:** the high share of unknown R1 jobs makes "0 identified automatically" weaker for X6 than for X5.

## `742cc445` and `97a7dfcf` (N1 ranks 4 and 5): close looks (23 Nov 2026, during X6, recorded 07:17 UTC; post hoc)

Commands: `podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/742cc445_checks.py` (parts 1–3)
and `notes/97a7dfcf_checks.py` (parts 1–2). Single-threaded E, 20–60 s per goal, run beside X6. Memos:
`notes/742cc445.md`, `notes/97a7dfcf.md`.

| Check | `742cc445` | `97a7dfcf` |
| --- | --- | --- |
| laws | x·(y∘(x∘z)) = x (McKenzie's L1); x∘((x∘y)·(z∘x)) = x | x·x = y·y; x·(y∘x) = x∘y; (x·y)·z = y∘(z·y) |
| plain reading | not found; C (4 short consequences) does not give back either law | equivalent to 0 = x·x, (x·y)·z = 0, x∘(y·z) = 0, x·(y∘x) = x∘y (E both ways) |
| emergent | 8 short laws, incl. x·(x∘y) = x and idempotence, each needing both axioms | all depth-2 products but x·(y·z) and x·(y∘z) vanish |
| key structural fact | ∘ associative ⇒ · = ∘ = left projection (E), so no band-based model | – |
| lattice? | law 1 holds in the 2-element lattice, law 2 fails under both readings | – |
| shadow (· = ∘) | left-zero band; ETP 54 and 828 (checked by `law_index`) | null semigroup (E) |
| literature | web-only agent: no source for T or for subsets of McKenzie's basis; Leech's families are band-based, Padmanabhan's and Fried's commutative | zeropotent algebras only (earlier search) |

**Verdict:** both not identified. `742cc445` is the more interesting of the two. It is near lattices and bands without
being either, and its synergy needs both laws. The funnel's level 8 is now 4. Still to read for `742cc445`:
McCune–Padmanabhan, LNCS 1095, pp. 137–150.

## The two filters X5 called for (23 Nov 2026, recorded 06:28 UTC; built and measured post hoc, nothing re-ranked)

Code: `soup/hidden.py` (`hidden_param`, `--param`), `soup/offdiag.py` (`IGNORE2`), arm `fusion3`
(`soup/stream/searcher.py`), verifier V6 (`soup/verify.py`). Tests: `tests/test_x6_filters.py` (4 tests; whole suite 75,
all pass).

**1. Definitions with a parameter** (`hidden_param`, the V6 screen). It searches terms in one operation over x, y and
the constant squares z·z and z∘z (size ≤ 4) for one that agrees with the other operation on the models (Mace4 sizes
2–4, at most 300 per size; in V6, the census). E proves the definition (30 s; 10 s in V6), and only a proof counts.
Terms that agree on every model are merged, but up to 6 alternatives are kept: the first version tried only one, and
missed 2 of the 16 known cases.
- On all 158 candidates (`soup.hidden --param --set candidates`, 3 min, `work/check/hidden_param.log`): **18 of
  X5's 20, and 0 of the other 138.** That covers the 16 found by hand (ledger row 12) and 2 more.
- Controls: `55cb2c91` and the absorption pair are not caught (test).

**2. Ignored variables that occur more than once** (`IGNORE2`, arm `fusion3`). A law L = R in which R is L with every
occurrence of one variable replaced by another variable, new or already in L. Then L does not depend on that variable.
- 187 laws, against IGNORE's 53. It contains IGNORE, X5's attractor x·(x·x) = y·(x·y), and constant squares x·x = y·y.
- **On the candidates, 151 of 158 imply an IGNORE2 law** on their run's corpus. Every run is affected (X5 all 20; X3 16
  of 19), and so are `55cb2c91` (x·(y·z) = x·y) and the absorption-type theories.
- The 7 that pass are Latin-square-like: `f8d1f554` and `3e068fa6` (half of the Δ-bijective core), `e430cc74`,
  `154e991a`, `fab766d9`, `57f39f2c`, `1f92a593`.
- So `fusion3` is a strong restriction: to "fully rigid" theories, the quasigroup and Yang–Baxter corner.

**Smoke run** (4 min, arm `fusion3`, V6, seeds 991–994, data deleted afterwards): 15 theories verified, 7 with a
positive score, and 2 caught by the parameter screen (no screen errors). Skips: 4.3% lattice-valid and about 7%
IGNORE2.

**Reading:** the first filter is exact on what it was built for, with no collateral. The second redefines the
search region. Whether X6 should use it is a design choice for its preregistration, not a fix.

## T6: S12 ⇒ x·x = x∘x, long prover runs (23 Nov 2026, 00:28–02:30 UTC)

Command: `podman run -d --name soup-s12 -v "$PWD/work:/data" -v "$PWD/notes:/notes:ro" -e PYTHONPATH=/app soup python3
/notes/s12_long.py`. Four jobs in parallel, 7,200 s each, which is four times round 2's 1,800 s. Every prover ran under
2,000 MB. Full outputs are in `work/check/s12_long/`, not tracked: Twee's is 6 MB. `summary.json` and the FMB log are
tracked.

| Job | Result |
| --- | --- |
| Vampire FMB (`-sa fmb`) | no model on sizes 1–6; size 7 still in SAT solving at 7,200 s |
| Vampire portfolio `casc_sat` | Timeout |
| Vampire `casc` | Timeout (no proof) |
| Twee 2.7.1 | killed at 7,320 s, no proof; 1.6 M critical pairs queued |

**Verdict:** still open, with these budgets. No finite countermodel exists on ≤ 6 elements; that is now both Mace4's
(round 2) and Vampire FMB's result, and size 7 is unsearched. No prover found a proof in 2 h. Caveats:
- The run overlapped X5's post-run checks (split, dedupe, digs), so the machine was not idle.
- S12 ⇒ x·x = x and ⇒ x∘x = x are refuted by the 10-element model of round 2. That model satisfies x·x = x∘x.

## X5: the fusion arm restricted to rigid theories (22 Nov 2026, 21:39 UTC – 23 Nov, 00:10 UTC; preregistered)

Preregistration: PREREGISTRATION.md, X5 (commit `5a04726`, before the start; timestamp corrected in `e6690f2`). The
single change from X4: arm `fusion2` skips every theory whose corpus-implied laws contain an argument-ignoring law
(`soup.offdiag.IGNORE`, 53 laws). Commands:
- run: `podman run -d --name soup-x5 -v "$PWD/work:/data" -e SOUP_DATA=/data/x5 -e SOUP_VERIFIER=V5 soup python3 -m
  soup.stream.supervisor --arm fusion2 --searchers 4 --verifiers 4 --seed0 801 --budget 9000 --run x5`;
- fragments: `-e SOUP_DATA=/data/x5 -e FRAG_JOBS=6 soup python3 -m soup.fragments`;
- statistics: `notes/runstats.py x5`, `notes/diagonal.py x5`, `notes/heartbeats.py x5`, `notes/x5_predictions.py`
  (written during the run, committed before any result was read; outputs `notes/*_x5.out`, `notes/x5_predictions.out`).

| | X5 (fusion2, V5) | X4 (fusion, V5) |
| --- | --- | --- |
| verified theories | 292 (117 per hour) | 636 (254 per hour) |
| positive score | 164 | 565 |
| fragments of a named theory | **0 of 164** | 0 of 565 |
| screened by V4 | 13 split, 0 division | 3 split, 0 division |
| skipped: lattice-valid / argument-ignoring | 75,334 / 80,166 of 2,588,072 evaluations (2.9% / 3.1%) | 70,453 (2.2%) / not applicable |
| claims / proved | 477 / 274 | 1,309 / 955 |
| refuted by finite models (stages a and c, and FMB) | 114 (24% of claims) | 276 (21%) |
| refuted by Vampire FMB | 79 (sizes 6 ×5, 7 ×10, 8 ×27, 10 ×37; FMB ran on 159 claims) | 22 |
| refuted by E saturation | 9 (8 uncertified) | 40 (15 uncertified) |
| unknown / open | 76 / 4 | 13 / 3 |
| proving emergent associativity / commutativity | 0 / 92 | 0 / 7 |
| structures added to the corpus | 437 | 3,844 |

**Predictions** (`notes/x5_predictions.out`):
- **P1 holds.** 0 of 164 scored theories imply an argument-ignoring law on X5's final corpus (X4: 519 of 565).
- **P2 holds.** X5's ten most frequent proved emergent laws share none with X4's.
- **P3 holds.** 120 of 164 (73%) have a proved claim with a square subterm, against 483 of 565 (85%).
- **P4 holds, in the direction the caveat feared.** All 20 top non-fragments have the same 9 classical models, affine
  structures over 𝔽₄ (`notes/disconnected_x5_x4.out`). "Disconnected" marks: **X5 0 of 20**, X4 14 of 20.

**A new attractor.** The most frequent proved law is x·(x·x) = y·(x·y) (88 of 164). A term ignores a variable that
occurs twice, which the IGNORE definition misses: it renames only variables that occur once. Commutativity of each
operation is proved in 92.

**Post-run checks** (23 Nov, 00:14–01:20 UTC; log `work/check/x5_post.log`):
- **Candidates.** X5's top 20 joined the pool: 158 candidates (`dossier candidates --sources
  t4-prior,t4-noprior,.,x1,x2,x3,x4,x5`). T5a ranks of X5's 20: 69, then 121–156 of 158.
- **Equivalence checks** (`notes/cand_checks.py x5`, output `notes/cand_checks_x5.out`): `soup.hidden` 0
  definitional; `soup.relabel` 0 relations.
- **Split.** `soup.split --set candidates` (capped at 1,800 s) stalled on one of X4's three unchecked candidates and
  checked none of X5's. It was rerun per candidate (`soup.split --laws`, 300 s each, 4 in parallel; output
  `notes/split_x5_candidates.out`): 0 split, 1 not split (finite certificate), 19 undecided.
- **R1** (`soup.rediscover --sources x5 --jobs 6`, 90 E jobs, 47 unknown): no theory is a fragment of, or equivalent
  to, a catalogue entry; 6 are subvarieties of doppelsemigroups; top 20: 0 identified by the automatic checks.
- **Dedupe** (`soup.dedupe --jobs 4`, x5 added to the corpora): 158 candidates are **125 varieties**. X5's 20 are
  5 varieties, one of them holding 15 candidates.

**What X5's candidates are (post hoc, by hand; ledger row 12).** Script: `notes/x5_top3_probe.py`, parts 1–3, E
20–30 s per law, output `notes/x5_top3_probe.out`.
- In 19 of 20, · is a **Steiner loop**: E proves x·y = y·x, x·(x·y) = y and x·x = y·y, and the constant square is then
  an identity.
- In 16 of 20, E proves x∘y = (x·y)·(z∘z) and x·y = (x∘y)∘(z·z). So ∘ is the same loop translated by ∘'s identity:
  a one-operation structure with a parameter. `soup.hidden` misses this disguise because its terms have no constants.
- The other 4 are undecided in that budget (one has no Steiner-loop proof).

**Reading.** Restricting to rigid theories took the search out of the lattice-and-band region and away from X4's
attractor, as intended. It landed on a classical one-operation structure in a new disguise. The run found no
disconnected candidate. Two filters follow from it, neither applied post hoc to the ranking:
1. extend `soup.hidden` to terms with a constant (z·z, z∘z);
2. extend IGNORE to variables that occur more than once.

The live table (N1) lists the X5 entries with this identification in its literature column. Its five X5 varieties enter at
ranks 23–27 of 82 (a classical model each); the top 10 is unchanged. Following N1's
preregistered gate, the gate itself is not changed.

## `1d0a5211` (N1 rank 2): what the theory is (22 Nov 2026, evening, recorded 21:45 UTC; post hoc)

Command: `podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/1d0a5211_checks.py`, parts 1–3
(output `notes/1d0a5211_checks.out`). Memo: `notes/1d0a5211.md`. T = {(A) x·(x∘y) = y∘x, (B) (x∘(y·z))∘z = z}.

| Check | Result |
| --- | --- |
| short consequences (order ≤ 3, suggested by the corpus) | 22 proved by E (20 s each), 4 of them emergent, all from x·(x∘(y·x)) = x |
| where they come from | B alone gives (x·y)∘y = y, in one superposition of B into itself (E proof object). A turns x·(x∘(y·x)) into (y·x)∘x, and that is x |
| A + (x·y)∘y = y ⟹ B? | no proof (E, 120 s) |
| not implied (E, 30 s each) | x·x = x, x∘x = x, (x∘y)∘y = y, x∘(x·y) = y, (x·y)·y = x·y, x·(y·x) = x, (x∘y)·y = x, x·(y∘x) = x |
| with x·y = x∘y | x·y = x and x·y = y (E): only one-element models; no shadow model with x·y ≠ x on 2–6 elements (Mace4) |
| non-degenerate models, sizes 2 / 3 / 4 / 5 | 0 / 7 / ≥ 669 / ≥ 2,971 (`soup.profile`, dossier) |
| literature (targeted web-only agent; key claims rechecked) | with · = ∘, A is ETP 335 = Stein's first law x(xy) = yx, and B is ETP 238 (both mappings checked by `law_index`); no source for B or for T |

**Verdict:** not identified; related in pieces. T splits Stein's law across two operations. Its synergy is real but
shallow, two rewriting steps, and its one-operation shadow is trivial, as for `55cb2c91`. Not run for this
candidate: Lean (no general statement emerged) and a proof that A + K does not imply B (E only failed to prove it).

## `55cb2c91` (N1 rank 1): what the theory is (22 Nov 2026, 20:00–20:50 UTC; post hoc)

Command: `podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/55cb2c91_checks.py`, parts 1–4
(output `notes/55cb2c91_checks.out`). Lean: `lean/Duet/T55cb2c91.lean`. Memo: `notes/55cb2c91.md`.
T = {x·(x∘y) = x, x·y = ((y·z)·x)∘x}.

| Check | Result |
| --- | --- |
| short consequences (order ≤ 3, suggested by the corpus) | 30 proved by E (20 s each), 13 of them emergent, e.g. (x·y)·y = x·y and x·y = (y·x)∘x |
| T ⟺ C: x·(y·z) = x·y, x·(x∘y) = x, x·y = (y·x)∘x | E both ways, 60 s per law; (x·y)·y = x·y is redundant in C; Lean `C_implies_T` |
| which · occur | exactly those with x·(y·z) = x·y, (x·y)·y = x·y, every x a value of x·−, and y·x = y'·x ⇒ x·y = x·y' (Lean `reduct_iff`, for every type); the prediction matches brute force on all 63 tables on 3 elements; the first version, without (x·y)·y = x·y, failed on 6 |
| what ∘ is | forced on pairs (y·x, x), where it is the swap y·x ↦ x·y; free elsewhere, inside {w : u·w = u} |
| with x·y = x∘y | ETP 4174 alone gives a constant operation; with ETP 9, only one-element models (E) |
| non-degenerate models, sizes 2 / 3 / 4 / 5 | 0 / 5 / ≥ 365 / ≥ 2,099 (`soup.profile`; 4 and 5 capped) |
| literature (targeted web-only agent; the collapse rechecked by E) | x(yz) = xy is ETP 327 and (xy)y = xy is ETP 378; with idempotence they are a basis of Waldhauser's minimal-clone varieties (arXiv:1102.2127, excerpts); no source for the theory, the conditions on ·, or the swap |

**Verdict:** not identified; related in pieces. A two-operation theory whose one-operation shadow is trivial. Its ·
has named laws (ETP 327, 378), and its ∘ is a partial swap. Lean: `lean/check.sh` passes 27 modules, and the axiom
audit passes on 290 declarations.

## `a9295908` (N1 rank 3): what the theory is (22 Nov 2026, 19:05–19:54 UTC; post hoc)

Command: `podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/a9295908_checks.py`, parts 1–6
(output `notes/a9295908_checks.out`). Lean: `lean/Duet/A9295908.lean`. Memo: `notes/a9295908.md`.
T = {x·(x∘x) = x, (x∘y)·y = y, x·y = x∘(y·x)}.

| Check | Result |
| --- | --- |
| T ⟺ C: · commutative and idempotent, x∘(x·y) = x·y, (x∘y)·y = y | E both ways; Lean `T_iff_C`, a hand proof; T also gives x∘x = x |
| · associative? | no: E and Vampire saturate, and Mace4 finds a 3-element model with ∘ the right projection (Lean `not_assoc`, `decide`) |
| ·-reducts of the models | exactly the commutative idempotent groupoids (∘ = right projection gives every one) |
| when · is a semilattice meet | T ⟺ (y ≤ x ⇒ x∘y = y) ∧ (y ≤ x∘y) (Lean `inf_iff`) |
| models from order theory | x∘y = (y if y ≤ x, else ⊤) on every meet-semilattice with a top (Lean `threshold_model`); **every Heyting algebra, with x∘y = (y→x)→y** (Lean `heyting_model`; also (x→y)∧((y→x)→x); both checked on 7 finite Heyting algebras) |
| models up to isomorphism, sizes 2 / 3 / 4 / 5 | 1 / 14 / ≥ 2,107 / ≥ 11,794 (4 and 5 capped); on 3 elements, 3 with · associative and 7 with ∘ the right projection, which matches the 7 commutative idempotent groupoids on 3 elements (counted independently) |
| literature (targeted web-only agent; key claims rechecked) | on chains, ∘ is the strict-order connective of Gödel logic, (A⊃B)∧((B⊃A)⊃A) (Baaz, Ciabattoni and Zach, LPAR 2000, §2); no source for T itself |

**Identification (ledger row 11).** T is valid in every Heyting algebra under a term interpretation, so it is a
fragment of Heyting-algebra theory written in ∧ and the strict-order connective, without associativity. The
synergy left is that three bridge laws force · to be commutative and idempotent. Open: whether T plus associativity
of · is exactly that fragment. Lean: `lean/check.sh` passes 26 modules (with `A9295908`), and the axiom audit passes on 284
declarations, `heyting_model` included.

## N1: a novelty ranking next to T5a, and the candidates up to equivalence (22 Nov 2026, 18:09–18:24 UTC; post hoc)

**Dedupe** (`soup.dedupe --set candidates --jobs 6`, 25 s for the proofs; `work/check/dedupe_candidates.json`). Since
the afternoon the model filter uses the corpora of all runs (26,708 found structures), not the main one only.
- 58 (pair, relabelling) pass the model filter, and E proves 51 of them both ways.
- **138 candidates are 120 varieties**: 14 classes have more than one member. Many members are the same theory written
  in dual form by different runs.
- **One variety was reached three times:** `2dc27508` (the early runs), `69dfbd8e` (X2) and `31d6d970` (X3).
  - The equivalence was rechecked by hand: E both ways under rev∘ and under rev·, and 8 models on 3 elements and
    325+ on 4 for both.
  - The non-degenerate counts differ (6 against 4 on 3 elements) because the non-degeneracy test (· ≠ ∘) is not
    invariant under relabelling.
  - So the identification of `31d6d970` covers this variety: with associativity it is the rectangular skew
    lattices.
- Other classes:
  - `3e068fa6` with `f8d1f554` (X1);
  - T5a's rank 7, `c8e6ca60`, with `b302a8c7`;
  - X3's `5c6da20c` with X2's `2e73bcd0`;
  - X3's `154abc19` with `c1760e50` (t4-noprior).

**N1** (PREREGISTRATION.md, N1, written before computing, with one clarification before computing: a partial
identification applies to the whole dedupe class). Command: `podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes"
-v "$PWD/README.md:/repo/README.md" soup python3 -m soup.novelty --readme /repo/README.md`. Outputs:
`work/check/novelty_ranking.json`, `notes/candidates_table.md`, and the README's live section.

| gate | candidates |
| --- | ---: |
| pool | 138 |
| no verification record (T1, T2) | 2 |
| identified (known): related to a named or catalogued structure 35, split 14, same variety as another candidate 6, ledger 1 | 56 |
| fail "works" | 3 |
| **enter N1** | **77** |

- **The top 10 shares no member with T5a's top 10.**
- **Runs in the top 10:** N1 has X4 7, the early runs 2 and t4-prior 1. T5a has x1 3, x2 2, the early runs 2,
  t4-prior 2 and x3 1. The preregistered expectation (X4's share larger in N1) holds: 7 against 0.
- **All of N1's top 20 have an off-diagonal proved emergent law and no classical model.** In all, 22 of the 77 have an
  off-diagonal law. The classical-model mark hardly separates anything: 6 of the 77 and 6 of the 56 known candidates
  have a structured model on 3 or more elements.
- **N1's top 3 come from runs that did not select for off-diagonal laws:**
  - `55cb2c91` (early runs);
  - `1d0a5211` (early runs);
  - `a9295908` (t4-prior), whose emergent laws include the commutativity of ·.
- **Follow-up:** dossiers `work/dossiers/n1-01…10-*.md` (`dossier write --top 10 --order n1`), and Lean
  certificates Cand14–23 for the smallest models. `lean/check.sh` passes 25 modules, and the axiom audit passes on 272
  declarations.
- **Structure of the top 10** (`notes/n1_structure.py`, E 10 s per goal; output `notes/n1_structure.out`):
  - four are idempotent with an absorption law, near the absorption family (`742cc445`, `f79a5097`, `7c476118`,
    `a8963027`);
  - three have almost constant smallest models, nilpotent-like (`97a7dfcf`, `7ec7f8f5`, `3b3b1176`);
  - `a9295908` has a commutative idempotent · whose 3-element model is a chain semilattice;
  - `55cb2c91` and `1d0a5211` have no standard law among those tested.
- **Literature checks** of the top 10, by two web-only agents. Their key claims were rechecked by machine:
  2-element-lattice failures, model checks and E proofs. The verdicts are in `work/check/literature.json`, the N1
  dossiers and the tables.
  - **No source for any of the 10.** Two are related only: `742cc445` contains McKenzie's lattice law L1, and
    `f79a5097` shares two absorption identities with Leech's skew lattices, which are associative where it is not.
  - **Collapses with x·y = x∘y** (E): `7ec7f8f5` becomes a constant operation; `7c476118` becomes the left
    projection; `a8963027` becomes exactly ETP Equations 9 ∧ 10, proved both ways; `f79a5097` implies Equations 9
    and 10.
  - **`a9295908`: a lead at first, then identified** (dug into the same evening; see below). Its 3-element model is
    the meet of a chain with Gödel implication changed on the diagonal (x∘x = x). The same construction gives a model
    on every chain of 3 to 6 elements.
  - Searched: the web, zbMATH, the McCune–Padmanabhan monograph's contents, Veroff's lattice-basis page, the ETP
    equation list, and Leech 2020 (pp. 31–32). Several sources were not read in full; each note says which.

Caveats:
- N1 is post hoc and descriptive. Its gate sees only our checks, our catalogue and the ledger.
- Its first key favours X4 by construction.
- "Not known" in the table means not identified by those; it is not "new".

## X4: fusion arm, away from the diagonal (22 Nov 2026, 13:01–15:31 UTC; descriptive)

Preregistered as exploratory (PREREGISTRATION.md, X4; deviation 6). Arm `fusion` with verifier V5, seeds 701–704,
4 searchers and 4 verifiers, budget 9,000 s, its own data directory (starting corpus 4,252 found structures).
- **Ran to budget**, exit code 0. The minimum available memory was 1,627 MB.
- **First attempt `x4a`** (12:55–12:58 UTC), stopped after 3 minutes: 10 of its 18 positive results proved
  `x·x = y·y` (`notes/diagonal_x4a.out`). The diagonal was then widened to laws in which each side has at most one
  variable, and the run restarted (deviation 6).

Commands:
- run: `podman run -d --name soup-x4 -v "$PWD/work:/data" -e SOUP_DATA=/data/x4 -e SOUP_VERIFIER=V5 soup python3 -m
  soup.stream.supervisor --arm fusion --searchers 4 --verifiers 4 --seed0 701 --budget 9000 --run x4`;
- fragments: `-e SOUP_DATA=/data/x4 -e FRAG_JOBS=3 soup python3 -m soup.fragments`;
- statistics: `notes/runstats.py x4`, `notes/diagonal.py x4` and `notes/heartbeats.py x4` (outputs `notes/*_x4.out`).

| | X4 (fusion, V5) | X3 (prior, V4) |
| --- | --- | --- |
| verified theories | 636 (254 per hour) | 970 (375 per hour) |
| positive score | 565 (each with a proved off-diagonal emergent law, by construction) | 833 |
| fragments of a named theory | **0 of 565** | 263 of 833 (31.6%) |
| screened by V4 | 3 split, 0 division | 47 split, 36 division |
| skipped as lattice-valid | 70,453 of 3,267,852 evaluations (2.2%) | not applicable |
| claims / proved | 1,309 / 955 | 3,002 / 2,664 |
| refuted by finite models (stages a and c) | 276 (21% of claims) | 89 (3%) |
| refuted by Vampire FMB | 22 (sizes 6 ×5, 7 ×9, 8 ×3, 9 ×1, 10 ×4; FMB ran on 46 claims) | 15 |
| refuted by E saturation | 40 (15 uncertified) | 175 (58 uncertified) |
| unknown / open | 13 / 3 | 56 / 3 |
| proving a one-variable emergent law | 0 (by construction) | 810 of 833 (97%) |
| proving emergent associativity / commutativity | 0 / 7 | 0 / 9 |
| structures added to the corpus | 3,844 | — |

**Preliminary reading:**
- **The run left the named corner.** No theory is a fragment of a named theory.
- **It works on less charted ground.** Finite models refute 21% of its claims, against 3% in X3. The corpus guesses
  for off-diagonal laws are weaker, and the corpus grew by 3,844 structures.
- **The attractor moved, it did not disappear.** The most frequent proved laws are x·(x·x) = x·(x·y) (104),
  x·(x·x) = x·(x∘y) (86), x·(x∘y) = x·x (61) and x·(x·y) = x·x (61). A left translation sends a family of elements
  to x·x. These are two-variable laws that still pivot on the square.

**Post-run checks** (17:54–18:23 UTC):
- **Candidates.** X4's top 20 non-fragments joined the pool, which now holds 138 candidates (`dossier candidates
  --sources t4-prior,t4-noprior,.,x1,x2,x3,x4`).
- **Equivalence checks** (`notes/cand_checks.py x4`):
  - `soup.hidden`: 0 definitional.
  - `soup.relabel`: 0 relations to a named theory under the 8 relabellings.
  - `soup.split`: 14 not split (finite certificate) and 3 undecided. It was stopped before the last 3 (deviation 7),
    which passed V4's split screen during the run.
- **T5a ranking** (`work/check/ranking.txt`). X4's candidates land at ranks 34, 35, 36, 110, 116, … 136 of 138, so the
  top 10 is unchanged and needs no new Lean certificates or dossiers. T5a prefers a convergent presentation and a
  duality; X4's theories have no duality by design.
- **R1 on X4** (`soup.rediscover --sources x4 --jobs 6`, 534 s, 437 E jobs, 106 unknown; summary in
  `work/check/rediscover_summary.txt`):
  - none of the 636 theories is a fragment of, or equivalent to, a catalogue entry;
  - 3 are subvarieties of dimonoids and 5 of doppelsemigroups;
  - the top 20 candidates: **0 identified** (X3: 5 of 19, 26%; X2: 9 of 18, 50%).
- **"Disconnected" marks** (preregistered, `notes/disconnected.py x4 x3`, output `notes/disconnected_x4_x3.out`): works,
  unconnected to every check, and no classical model. **X4: 14 of 20; X3: 10 of 19.** The measure sees only our checks
  and catalogue. One of X3's ten, `31d6d970`, is partly identified through the literature.
- **Off-diagonal baseline** (preregistered, `notes/offdiag_baseline.py x3`, output `notes/offdiag_baseline_x3.out`, on
  X3's final corpus). Without selection for it, 226 of X3's 833 positive theories (27.1%) prove an off-diagonal
  emergent law, and 673 (80.8%) have a non-empty off-diagonal gain on the corpus. X4: 565 of 565, by construction.
- **Split scan of X4's 565 non-fragments** (`-e SOUP_DATA=/data/x4 soup python3 -m soup.split --fragments 1 --jobs 4`,
  run last, 18:24–19:02 UTC): **0 split**, 408 not split (finite certificate), 157 unknown, 0 errors. X3: 0 of 570;
  X2, unfiltered: 33 of 654.

## X3: exploratory run with verifier V4 (22 Nov 2026, 08:33–11:08 UTC; descriptive)

Preregistered as exploratory (PREREGISTRATION.md, X3). It is X2 with verifier V4: split theories and divisions in
disguise score 0 in stage a. Seeds 601–604, arm `prior`, 4 searchers and 4 verifiers, its own data directory
(starting corpus 4,252 found structures). **Stopped by its memory rule after 9,304 of 10,200 s** (deviation 5): 975 MB
available at 11:08:32, with the supervisor's PSS total up from 7.1 to 8.3 GB in the last 22 minutes.

Commands:
- run: `podman run -d --name soup-x3 -v "$PWD/work:/data" -e SOUP_DATA=/data/x3 -e SOUP_VERIFIER=V4 soup python3 -m
  soup.stream.supervisor --arm prior --searchers 4 --verifiers 4 --seed0 601 --budget 10200 --run x3`;
- fragments: `-e SOUP_DATA=/data/x3 -e FRAG_JOBS=3 soup python3 -m soup.fragments`;
- statistics: `podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - x3 < notes/runstats.py` (output
  `notes/runstats_x2_x3.out`), and `notes/diagonal.py x3`.

| | X3 (V4) | X2 (V3) |
| --- | --- | --- |
| verified theories | 970 (375 per hour) | 1,015 (357 per hour) |
| screened by V4 (score 0) | 83: split 47, division 36 | not screened |
| with an emergent law | 833 | 948 |
| fragments of a named theory | 263 (31.6%): lattice 262, skew lattice 17, absorption pair 6, idempotent left quasigroup 1 | 294 (31.0%) |
| non-fragments | 570 | 654 |
| claims / proved | 3,002 / 2,664 | 3,425 / 3,022 |
| refuted by E saturation | 175 (58 uncertified) | 239 (80 uncertified) |
| refuted by finite models (stages a and c) | 89 | 86 |
| refuted by Vampire FMB | 15 (sizes 6 ×2, 7 ×9, 8 ×4; FMB ran on 75 claims) | 17 |
| unknown / open | 56 / 3 | 55 / 6 |
| scored theories proving a one-variable emergent law | 810 of 833 (97%) | (97% over T4–X3, `notes/diagonal_pre_x4.out`) |

The V4 screen took a median of 0.0 s; the slowest took 434 s.

**Preregistered descriptive outcomes:**
- **Throughput:** 375 against 357 verified per hour. The early lead (about 840 per hour in the first 22 minutes,
  when the screens removed many theories cheaply) did not last.
- **Fragment share:** unchanged, 31.6% against 31.0%. The screens remove disguises, not lattice fragments.
- **V4 marks:** 47 split and 36 division (8.6%). Consistency check: R1 on X3 finds exactly 36 theories that imply a
  one-sided quasigroup pair, the 36 that V4 marked as divisions.
- **Split scan of X3's non-fragments** (`-e SOUP_DATA=/data/x3 soup python3 -m soup.split --fragments 1 --jobs 4`, run
  last): 570 non-fragments, **0 split**, 440 not split (finite certificate), 130 unknown. X2 had 33 split of 654.
- **Identified share of the top-20 non-fragments** (`rediscover --summary --candidates`,
  `work/check/rediscover_summary.txt`): **X3 5 of 19 (26%)**, all absorption-type subvarieties (`soup.relabel`). X2 had
  9 of 18 (50%), and X1 11 of 19 (58%). With the split theories and divisions screened out, fewer of the top
  candidates are things the automatic checks recognise.
- **The top 20 in the ranking.** X3's top 20 non-fragments add 19 candidates (118 in all; one was already listed up to
  duality). In the T5a ranking they land at ranks 3, 12, 31, 38, 41, … 118 (`notes/cand_checks.py x3`, output
  `notes/cand_checks_x3.out`).
  - `soup.split`: 0 split (16 certificates of non-split, 3 unknown).
  - `soup.hidden`: 0 definitional.
  - `soup.relabel`: 5 imply an absorption pair, none implies a quasigroup pair, and none is a fragment of or
    equivalent to a named theory.

**R1 on X3** (`soup.rediscover --sources x3 --jobs 6`, 6 min, 2,259 E jobs, 51 unknown). The catalogue score is
unchanged: 7 of 13 entries rediscovered (7 of 12 without the post hoc entry).
- Exact equivalents to the absorption pair: 9, more than any earlier run (X2 5, T4 prior 7).
- Lattice: 262 fragments, no basis. Weakly associative lattices: 122 fragments.

**Rank 3, `31d6d970` = {x·(x∘y) = x, (x∘y)·y = y, (x·x)·(y·x) = x, (x·y)·(x·x) = x}** (`notes/31d6d970_checks.py`,
output `.out`; literature check by a web-only agent, key claims rechecked here; `work/check/literature.json`).
- **Structure (E).** Both operations are idempotent, and x·(y·x) = x = (x·y)·x holds. Associativity of either
  operation, commutativity and the rectangular-band law all fail in the 3-element model.
- **The associative case is known.** With (x·y)·z = x·(y·z) added, E proves that · is a rectangular band and ∘ its
  transpose, and the converse holds. Rectangular bands are term-equivalent to the rectangular skew lattices (Leech
  2020, Prop. 1.3.14), and laws 1–2 are Leech's absorption identities.
- **Without associativity,** ∘ is a connector: x·(x∘y) = x, (x∘y)·y = y. Zelinka's anticommutative conservative
  groupoids (1994), with ∘ their transpose, are models. So is the 3-element model, where ∘ is not the transpose.
- **No source was found for the full theory.** Two sources were not read. Candidate only. Lean: `Cand13`
  (3-element model, 6 non-implications); `lean/check.sh` passes 15 modules, audit 162 declarations.

Caveats:
- X3 is exploratory, and the comparisons with X2 are descriptive.
- X3 stopped at 91% of its budget.
- V4 changes which theories reach the top, so the identified share is not a measure of the search alone: the
  screened theories are identified too, at score 0.

## Coverage: how much of the space the searches touched (22 Nov 2026, 10:14 UTC; X3 still running)

`podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/coverage.py` (output: `notes/coverage.out`).

| data directory | verified | queued (seen) | cheap evaluations |
| --- | ---: | ---: | ---: |
| `.` (three test runs) | 354 | 7,714 | 2,832,376 |
| `t4-prior` | 1,050 | 2,440 | 5,842,907 |
| `t4-noprior` | 441 | 2,503 | 5,405,530 |
| `x1` | 521 | 5,551 | 9,744,990 |
| `x2` | 1,015 | 5,699 | 14,878,548 |
| `x3` (running) | 841 | 6,394 | 6,446,939 |
| **total** | **4,222** | **30,301** | **45,151,290** |

The search can form law sets of 1 to 6 laws out of 71,369: 2.5 × 10⁹ pairs, 1.1 × 10¹⁸ sets of four,
1.8 × 10²⁶ in all. Verified theories are 1.7 × 10⁻⁶ of the pairs alone; cheap evaluations are 2.5 × 10⁻¹⁹ of all
law sets.

Caveats:
- Law sets overcount varieties: many are equivalent or trivial, and how many distinct varieties there are is not
  known. Evaluations count repeats of one theory again. Both ratios are rough. On any count the explored part is
  tiny.
- The explored part is not a random sample. The duality prior (T4) steers toward symmetric, absorption-type,
  lattice-like theories, which is where human work on two binary operations is densest. Every top candidate
  identified so far was known (`notes/rediscovery.md`).

What this means for the claims:
- **"No source found" is weak evidence.** Human knowledge of this region is large, and our literature checks are web
  and zbMATH searches, not a survey. They already missed one prior source (the Δ-bijective core of `10c98c4b`, on the
  first pass). A theory counts as unnamed only after a check by someone who knows the field, not after our searches
  alone.
- **The rediscovery rate (R1) measures the search in a well-mapped corner.** It says nothing about how often the
  search would find something new elsewhere.
- **A tiny explored part is not a negative result.** Finding nothing new here does not show there is nothing new
  to find. Runs that leave the well-mapped corner (no prior, asymmetric theories, order 5) are a different
  experiment, still to be preregistered.

## R1: rediscovery against a fixed catalogue (22 Nov 2026, 07:56–08:31 UTC; post hoc, preregistered plan)

Plan and catalogue committed before computing (`534c1af`; PREREGISTRATION.md, R1). The catalogue is 13 known
two-operation structures: the 10 named theories of T3, doppelsemigroups, weakly associative lattices, and
Δ-bijective pairs (marked post hoc).

Commands: `podman run --rm -v "$PWD/work:/data" soup python3 -m soup.rediscover --sources . --jobs 6`, then
`--sources t4-prior,t4-noprior,x1,x2 --jobs 6 --wall 7200`, then `--summary --candidates`. Output:
`work/check/rediscover.json`.

Run:
- 3,381 verified theories, all with a non-degenerate model.
- 51 relabelled catalogue variants, with 6,860 Mace4 models of them on 2–4 elements used as the model filter.
- 11,748 E jobs, 371 of them unknown.
- 39 min wall clock; no theory was left out at the wall cap.

**Primary outcome: 7 of the 13 entries were rediscovered (a fragment or an equivalent at least once), and 7 of the
12 that are not post hoc.**
- Rediscovered: lattice, skew lattice, absorption pair, bisemilattice, idempotent left quasigroup, idempotent right
  quasigroup, weakly associative lattice.
- Not rediscovered: dimonoid, left quasigroup, right quasigroup, right absorption pair, doppelsemigroup, and
  Δ-bijective pair (post hoc). Each of these occurs only as something implied (a subvariety), never as a fragment.

| entry | . | t4-prior | t4-noprior | x1 | x2 |
| --- | --- | --- | --- | --- | --- |
| theories | 354 | 1,050 | 441 | 521 | 1,015 |
| lattice | 247 / 1 / 1 | 329 / 4 / 4 | 30 / 0 / 0 | 118 / 1 / 1 | 293 / 6 / 6 |
| skew lattice | 44 / 1 / 0 | 51 / 4 / 0 | 1 / 0 / 0 | 19 / 1 / 0 | 38 / 6 / 0 |
| absorption pair | 8 / 187 / 2 | 23 / 323 / 7 | 1 / 80 / 1 | 4 / 175 / 2 | 11 / 341 / 5 |
| bisemilattice | 4 / 1 / 0 | 17 / 4 / 0 | 0 / 0 / 0 | 3 / 1 / 0 | 11 / 6 / 0 |
| idempotent left / right quasigroup | 3 / 0 / 0 | 13 / 60 / 0 | 2 / 1 / 0 | 2 / 12 / 0 | 6 / 25 / 0 |
| weakly associative lattice | 138 / 1 / 0 | 129 / 4 / 0 | 12 / 0 / 0 | 58 / 4 / **3** | 159 / 6 / 0 |
| left / right quasigroup | 0 / 0 / 0 | 0 / 60 / 0 | 0 / 1 / 0 | 0 / 13 / 0 | 0 / 25 / 0 |
| right absorption pair | 0 / 202 / 0 | 0 / 254 / 0 | 0 / 39 / 0 | 0 / 160 / 0 | 0 / 305 / 0 |
| dimonoid | 0 / 0 / 0 | 0 / 6 / 0 | 0 / 0 / 0 | 0 / 24 / 0 | 0 / 24 / 0 |
| doppelsemigroup | 0 / 0 / 0 | 0 / 6 / 0 | 0 / 0 / 0 | 0 / 25 / 0 | 0 / 24 / 0 |
| Δ-bijective pair (post hoc) | 0 / 0 / 0 | 0 / 85 / 0 | 0 / 1 / 0 | 0 / 41 / 0 | 0 / 68 / 0 |

Cells are fragment / subvariety / equivalent counts of distinct theories, over all 8 relabellings.

**Exact rediscoveries (equivalent):**
- **Lattices**: 12 theories (1 + 4 + 1 + 6), each a different basis for lattices. X2 alone has six, for example
  {x·x = x, x∘x = x, x·(y·(x∘z)) = y·x, x∘(y∘(x·z)) = y∘x, ((x∘y)·z)·y = y·z, ((x·y)∘z)∘y = y∘z}.
- **Absorption pairs**: 17 theories.
- **Weakly associative lattices** (Fried and Grätzer 1973): 3 theories in X1, all commutative and all containing
  x·((x∘y)·(z∘x)) = x with its dual. A structure whose name we did not have in T3's list was found exactly.

**Positive controls pass.**
- R1's lattice fragments (as written) equal those of `fragments.json` in all five directories: 247, 329, 30, 118,
  293, with identical key sets.
- `10c98c4b` is a subvariety of the Δ-bijective entry.

**Top candidates identified by any route** (`--summary --candidates`; split, division, or any catalogue relation,
including "implies"): `.` 11/20, t4-prior 9/20, t4-noprior 4/20, X1 11/19, X2 9/18 (and pilot 0/2). That is 44/99
in all. "Identified" here is weak: implying an absorption pair counts. Equivalence is the strong form.

Caveats:
- Post hoc on existing data, with a catalogue we wrote after seeing the results (the Δ-bijective entry is marked
  as such).
- Only order-4 axiomatizations can be found at all.
- A fragment of a weak entry (weakly associative lattice, absorption pair) is weak evidence; most of them are also
  lattice fragments.
- "Not rediscovered" includes entries that no reachable theory could match. The search has no laws of order 5 or
  more, and its prior favours dualities.

## X2: second exploratory run with verifier V3 (22 Nov 2026, 04:21–07:12 UTC; descriptive)

Preregistered as exploratory (PREREGISTRATION.md, X2): as X1, seeds 501+, its own data directory, 10,200 s. It ran
to budget (exit 0). Nothing heavy ran alongside. No worker crashed; X1 had 5 SIGSEGV restarts. The VM's available
memory reached a minimum of 1,026 MB, 2 MB above the stop rule, with nothing else running. X3's budget was set
to match (PREREGISTRATION.md, X3).

Commands:
- run: `podman run -d --name soup-x2 -v "$PWD/work:/data" -e SOUP_DATA=/data/x2 -e SOUP_VERIFIER=V3 soup python3 -m
  soup.stream.supervisor --arm prior --searchers 4 --verifiers 4 --seed0 501 --budget 10200 --run x2`;
- fragments: `-e SOUP_DATA=/data/x2 -e FRAG_JOBS=3 soup python3 -m soup.fragments`;
- statistics: a read-only script over `work/x2/results`.

| | X2 | X1 (for reference, 1.5 h) |
| --- | --- | --- |
| verified theories | 1,015 (357 per hour) | 521 (347 per hour) |
| with an emergent law | 948 | 474 |
| fragments of a named theory | 294 (31.0%): lattice 293, skew lattice 20, bisemilattice 11, absorption pair 7, idempotent left/right quasigroup 6/5 | 118 (24.9%) |
| non-fragments | 654 | 356 |
| claims | 3,425 | 1,781 |
| proved | 3,022 | 1,522 |
| refuted by E saturation | 239 (80 uncertified) | 132 (39 uncertified) |
| refuted by finite models (stages a and c) | 86 | 68 |
| refuted by Vampire FMB | 17 (sizes 6 ×6, 7 ×3, 8 ×8; FMB ran on 80 claims) | 10 |
| unknown / open | 55 / 6 | 47 / 2 |

**Candidates.** X2's top 20 non-fragments add 18 new candidates; the other 2 were already listed up to duality. That
makes 99 in all.
- `soup.split`: 1 split (`5358ef8f`), and 17 with a certificate of non-split (on 2 / 3 / 4 elements: 4 / 12 / 1).
- `soup.hidden`: 0 definitional.
- `soup.relabel`: 8 imply an absorption pair (6 the absorption pair, 4 the right one, under some relabelling). None
  implies a quasigroup pair, so there is no division in disguise, and none is a fragment of or equivalent to a
  named theory.

So X2's candidates have fewer known disguises than T4's (7 split of 62) and X1's (6 of 19).

**T5a ranking of the 99** (`dossier rank`, 4 min 44 s; `work/check/ranking.txt`). X2's candidates land at ranks 3, 4,
11, 22, 23, 28, 34, … 83. Dossiers were written for the top 13 (`dossier write --top 13`), and Lean certificates
added for the two new top-10 entries (Cand11, Cand12). `lean/check.sh`: 14 modules, including the general proofs
in `Delta.lean`; the axiom audit passes on 151 declarations.
- **Rank 3, `69dfbd8e`, is the variety of rank 10, `2dc27508`**, found again from different laws. E proves both
  directions (as written, and under rev· rev∘). Both have the same 10-rule convergent presentation. The candidate
  list deduplicates up to the three dualities, not up to logical equivalence, so this variety is counted twice. It
  is a rediscovery inside the search: two runs with different seeds and corpora reached one variety.
- **Rank 4, `d1e1c31f`**: an absorption-type algebra (it implies the absorption pair with ∘ reversed), not related
  by implication to the others of that family under any relabelling (E). No source found.
- **Rank 11, `3e068fa6`**: E's convergent presentation has 3 rules, (x∘y)·(y∘x) = y, x·x = x and x∘x = x. That is
  half of the Δ-bijective core with both operations idempotent.
  - Every finite model satisfies the other half too, since an injective self-map of a finite set is bijective.
  - The equational theory does not: E's presentation is convergent and does not join the two sides, so some
    infinite model fails it.
  - `10c98c4b`, relabelled, implies it.

Notes: `work/check/literature.json`.

**Split scan of all 654 X2 non-fragments** (`-e SOUP_DATA=/data/x2 soup python3 -m soup.split --fragments 1 --jobs 4`,
run last, about 8 min): 33 split, 477 not split (finite certificate), 144 unknown, 0 errors. Among the decided ones
that is 6.5% split, close to T4's prior arm (6.2%). So the search keeps producing split theories at the same rate
when nothing filters them; X3's verifier V4 does.

Caveats: X2 is exploratory, and the comparisons with X1 are descriptive. X2's starting corpus did not include X1's
finds.

## `10c98c4b`: structure and literature memo (22 Nov 2026, morning; post hoc)

Command: `podman run -i --rm soup python3 - < notes/10c98c4b_checks.py` (output `notes/10c98c4b_checks.out`; E, Mace4
and a complete enumeration; under a minute). Memo: `notes/10c98c4b.md`.

| Check | Result |
| --- | --- |
| B = {(x·y)∘(y·x) = x, (x∘y)·(y∘x) = x} ⟺ · orthogonal to its transpose, ∘ its decoder | hand proof; on 3 elements, 288 of the 3⁹ tables are orthogonal to their transpose, giving 62 B-models up to isomorphism (38 non-degenerate), the same as Mace4 |
| under B, (x∘y)·x = x ⟺ x·(x·y) = x·y, and the same for the other three absorptions | E, both ways, each of the 4 |
| found laws ⟺ B + {x·(x·y) = x·y, (x·y)·y = x·y, x∘(x∘y) = x∘y, (x∘y)∘y = x∘y} | E, both ways; idempotence follows; none of the 4 follows from B and the other 3 (E saturates) |
| with ∘ = ·: rectangular bands are models; the laws do not imply (xy)z = xz or x(yz) = xz | E |
| non-degenerate models on 4 / 5 elements | 2 / 14 (Mace4, complete); no law of a short list (associativity, rectangular-band laws, absorptions, Schröder) holds in all of them |

So `10c98c4b` says: · is orthogonal to its transpose, and every translation of · and of its decoder is idempotent.
This is the opposite of a self-orthogonal Latin square, where every translation is bijective.

Literature. Sources: web search, zbMATH reviews, a delegated lookup, and two papers read by us (Shcherbacov,
arXiv:2206.12844; Bonatto, Kinyon, Stanovský and Vojtěchovský, arXiv:1910.02148, §2.5).
- **B is prior art.** A binary algebra is *Δ-bijective* when (x,y) ↦ (xy, yx) is bijective. That the inverse is Δ
  of a second, "dual" operation, which is exactly B, is stated for arbitrary operations in several places:
  - Dehornoy, Adv. Math. 282 (2015), arXiv:1403.3019, §1, the "involutivity laws" (read by us via ar5iv);
  - Foundations of Garside Theory, Lemma XIII.1.28 (read by a delegated lookup);
  - Bonatto et al., Lemma 2.10.

  The idea comes from Rump (Adv. Math. 193, 2005). All of these work with the right-cyclic law or bijective left
  translations.
- **Not a Yang–Baxter solution.** None of `10c98c4b`'s 16 non-degenerate models on 4 and 5 elements makes r(x,y) =
  (x·y, y·x) satisfy the braid relation. The 2×2 rectangular band and the flip, used as controls, do (part 7 of the
  script).
- With ∘ = ·, B is Schröder's second law. Schröder quasigroups are well studied; the idempotent ones exist exactly
  for n ≡ 0, 1 (mod 4), n ≠ 5, 9 (Bennett, Wei and Zhu 1996).
- Belousov (1983, English 2005) classifies the identities that force a quasigroup to be orthogonal to a parastrophe.
- Orthogonality of arbitrary binary operations is studied too (Mullen and Shcherbacov 2005), as are "self-orthogonal
  n-ary groupoids" (Syrbu 1994).

The search rediscovered B. We found no source for the full theory: Δ-bijective groupoids whose translations, and
those of the dual, are idempotent. The Δ-bijective papers we saw are about left quasigroups, and no non-degenerate
model here is one. **Still a candidate:** Rump 2005, Dehornoy et al. 2015 (Ch. XIII), Evans, and Bennett and Zhu
1992 were not read.

Caveat: post hoc, on one candidate chosen after the ranking.

## Process notes and corrections (22 Nov 2026, night)

- **Model count of B (corrected 22 Nov, morning).** The `10c98c4b` literature note and dossier said that B alone has
  40 non-degenerate models on 3 elements. It has 38 (Mace4, and an enumeration of all 3⁹ tables). The wrong number
  was in commit `2255b8e`, which is pushed.
- **Paper abstract (corrected 22 Nov, morning).** It said that the duality prior "triples" the fragment share. 33%
  against 8% is a factor of 4.2; the abstract now gives the two numbers.
- **`10c98c4b` "no source found" (corrected 22 Nov, morning).** The night's note said that no source was found for
  B. B is prior art (Δ-bijective algebras, Rump 2005; Bonatto et al.). The night's searches had looked only in the
  Latin-square literature. The first draft of the memo also gave the wrong author (Belyavskaya) for the Mullen and
  Shcherbacov 2005 survey.

- **Rule 1 (host commands).** Three times a `python3` ran on the Mac instead of in the container. Twice it was
  an empty `python3 -`, which did nothing (21 Nov evening, 22 Nov about 01:33 UTC). Once it was a read-only
  `python3 -c` that loaded `work/check/literature.json` to check that it parses (22 Nov about 04:15 UTC). Nothing
  was installed or changed on the host.
- **T5a launch.** The first start of the T5a profile stopped on a `KeyError` for the 2 T3 theories whose
  verification had crashed: they have no `laws` field. It was fixed (`9dd1b79`, laws taken from the law indices)
  before any profile was computed.
- **T4 crashes.** A first version of the T4 section said no worker crashed. Four did, and all were restarted (T4
  section).
- **Split count.** A status message gave 6 split theories among the 62 candidates. There are 7: rank 6,
  `b302a8c7`, had been missed.
- **X1** was stopped by its memory rule (deviation 4). The most likely cause is the two split scans I started next
  to it.

## X1: exploratory run with verifier V3 (22 Nov 2026, 02:20–03:50 UTC; descriptive)

Preregistered as exploratory (PREREGISTRATION.md, X1): duality-prior arm, 4 searchers and 4 verifiers, seeds 401+,
its own data directory, verifier V3 (V2 plus Vampire finite model building on the claims that stage a leaves open).
**It ran 1 h 30 min of the planned 4 h.** The preregistered memory rule stopped it at 03:50 UTC, when the VM had
170 MB available (deviation 4). The most likely cause is the two post hoc split scans I had started two minutes
earlier. It was not restarted. 5 verifiers exited on SIGSEGV (02:26, 03:07, 03:25, 03:34, 03:39); the supervisor
restarted each and put its claimed task back.

Commands: `podman run -d --name soup-x1 -v "$PWD/work:/data" -e SOUP_DATA=/data/x1 -e SOUP_VERIFIER=V3 soup python
-m soup.stream.supervisor --arm prior --searchers 4 --verifiers 4 --seed0 401 --budget 14400 --run x1`; fragment check
`... -e SOUP_DATA=/data/x1 -e FRAG_JOBS=3 soup python -m soup.fragments`. Journal: `work/x1/journal/`.

| X1 | |
| --- | --- |
| theories verified (all V3) | 521 |
| with a proved emergent law | 474 |
| fragments of a named theory | 118 (24.9%), all of them lattice fragments (also skew lattice 11, absorption pair 3, bisemilattice 3, idempotent one-sided quasigroups 2 + 2) |
| not fragments | 356 |
| emergent claims | 1,781: 1,522 proved, 132 refuted by E saturation (39 of them without a confluence certificate), 68 by stage a's finite models (sizes 3–6), 10 by Vampire FMB, 47 unknown, 2 open |
| Vampire FMB | ran on 59 claims; refuted 10, on 5, 6 (2), 7 (6) and 8 elements |

Not compared with T4, as preregistered: the corpus was larger at the start, the verifier differs, and the run is
shorter. Vampire FMB settles claims that stage a cannot reach. Its 10 refutations in 1.5 h are on sizes 5–8. Stage a stops at size 6, and
it did not finish sizes 5 or 6 for those claims (`cm_unknown_sizes`).

The top 20 non-fragments by score went into the candidate list (81 candidates in all, 19 of them new; `b302a8c7`
was already in). Their profiles, equivalence checks and ranking are below.

## Candidates after the ranking: equivalence checks, literature, Lean (22 Nov 2026, early morning; post hoc)

These checks were written after the T5a ranking had been seen and are **not part of the preregistered rubric**.
They follow rule 4: no theory is called new without an equivalence check and a literature check. The standard list
of `soup.equiv`, the 10 named theories as written and the three dualities miss three ways a theory can be old:
- **hidden definition** (`soup.hidden`): one operation is a short term in the other. Terms of size ≤ 5 are
  evaluated on all models of sizes 2–4, then E proves any match;
- **split** (`soup.split`): the theory is a ·-theory plus a ∘-theory, and its bridges only look like bridges.
  - Certificate for *not split*: the · table of one model and the ∘ table of another fail a law. If the theory were
    V(·) ∪ W(∘), every such pair would be a model.
  - Proof of *split*: E derives every law from one-operation consequences of order ≤ 3;
- **relabelling** (`soup.relabel`): the named theories under all 8 relabellings (swap the operations, reverse ·,
  reverse ∘). Implications in either direction count only with an E proof (30 s each).

Commands: `podman run -d -v "$PWD/work:/data" soup python -m soup.{hidden,split,relabel} --set candidates`
(output `work/check/{hidden,split,relabel}_candidates.json`). Tests: `tests/test_hidden.py`, `tests/test_split.py`.

| check | 62 candidates (T4 and earlier runs) | 19 X1 candidates | all 81 |
| --- | --- | --- | --- |
| hidden definition: definitional | 0 | 0 | 0 (6 have a term that agrees on all models; E proves none) |
| **split** (E proof) | **7** | **6** | **13** |
| not split (finite certificate on 2 / 3 / 4 elements) | 55 | 13 | 68 (7 / 53 / 8) |
| relabelled named theory implied | 17 | 5 | 22: absorption pair 17, right absorption pair 10, one-sided quasigroups 4 |
| fragment of, or equivalent to, a relabelled named theory | 0 | 0 | 0 |

Split theories:
- from the earlier runs: `4dc33674`, `b302a8c7`, `adefe707`, `79bea529`;
- from T4 prior: `bbaf0199`, its top non-fragment by score;
- from T4 noprior: `2e6502d8`, `09184a57`;
- from X1: `c8e6ca60`, `695c2c2b`, `f5a5150b`, `0e846588`, `f85b2386`, `3c197ddc`.

An earlier status message gave 6 for the 62; the file gives 7. The syntactic bridge filter does not keep these
theories out, and both rankings put one of them first. `c8e6ca60` is the clearest case: E's convergent presentation
of it has no bridge at all.

**The top 10 of the preregistered ranking (81 candidates), after these checks.** Ranking:
`python -m soup.dossier rank` (`work/check/ranking.txt`). Dossiers: `python -m soup.dossier write --top 10`
(`work/dossiers/`), with details and sources. The E runs in the table are one-off checks: a scratch script, `fof`
axioms against a goal, 30 s, E 3.2.5. A saturation is CounterSatisfiable.

| rank | key | source | what it is |
| --- | --- | --- | --- |
| 1 | `4dc33674` | earlier | **Split**: equivalent (E, both ways) to {x·(x·y) = y, (x·y)·y = y} on · plus the mirror on ∘. Not a fusion. Its laws resemble those of bikei (Nelson–Rosenfield, arXiv:1603.02719), but it is not a bikei fragment. |
| 2 | `8a512957` | T4 prior | **An idempotent left quasigroup in disguise**: equivalent (E, both ways) to y∘x = x\y with x·x = x, x·(y·x) = y·x and (x·y)·y = y. Not a rack, not a twisted Ward left quasigroup, not a cycle set (E saturates on each). Its 3-element model and the affine model x·y = 2x + 3y on ℤ/4 (checked by evaluation) are quandles. No source for these identities in left quasigroups. Rank 19, `977c3603`, is the same without (x·y)·y = y. |
| 3 | `1ca933c1` | T4 prior | A subvariety of the named absorption pairs (both sides), and a proper subvariety of rank 7: E proves rank 7's laws from it and saturates the other way. Neither operation is associative or commutative (E saturates). |
| 4 | `c8e6ca60` | X1 | **Split**. |
| 5 | `87137d88` | X1 | In the same absorption family: a proper subvariety of rank 7, and incomparable with rank 3 (E). |
| 6 | `695c2c2b` | X1 | **Split**. |
| 7 | `3078949b` | earlier | A subvariety of the right absorption pair. E's convergent presentation (12 rules): both operations idempotent; x·(x·y) = x and (x·y)·y = x·y in each; the right absorptions; (x·y)∘x = x·y and (x∘y)·x = x∘y. |
| 8 | `2dc27508` | earlier | No relabelled named theory implied. · satisfies x·(y·x) = x and (x·y)·x = x (ETP 10, 25); ∘ alone satisfies only x∘x = x. Not split (2-element certificate). |
| 9 | `f5a5150b` | X1 | **Split**. |
| 10 | `10c98c4b` | X1 | **Transpose orthogonality with a decoder, plus absorption.** Equivalent (E, both ways) to B ∪ {(x∘y)·x = x, x·(y∘x) = x, (x·y)∘x = x, x∘(y·x) = x}, with B = {(x·y)∘(y·x) = x, (x∘y)·(y∘x) = x}. B says that (x,y) ↦ (x·y, y·x) is a bijection of A² with inverse (u,v) ↦ (u∘v, v∘u): · is orthogonal to its transpose, and ∘ decodes. With ∘ = ·, B becomes Schröder's second law (xy)(yx) = x. The four absorptions are (x∘y)·x = x and its three dual images, and none of them follows from B and the other three (E saturates). · is not Latin in any non-degenerate model. Non-degenerate models: 0, 0, 2, 14, ≥ 214 on 2–6 elements (Mace4, `soup.profile.all_models`; size 6 capped). |

Leaving the split theories out (post hoc), the top 6 are `8a512957`, `1ca933c1`, `87137d88`, `3078949b`,
`2dc27508` and `10c98c4b`. Two kinds recur:
- one-operation varieties written with a division: `8a512957` is a left quasigroup with extra identities, so it lies
  inside a named variety;
- absorption-type algebras without associativity: `1ca933c1`, `87137d88`, `3078949b`, plus `2dc27508` with a nearly
  free ∘.

`10c98c4b` is different, and it is the one we would show an algebraist. Its core B is a natural two-operation
condition (a groupoid orthogonal to its transpose, with the decoder as a second operation), and the search's
absorptions sit on top of it. Web searches (22 Nov 2026) found no source for B as a variety, nor for any of the six
law sets; the nearest named relatives are in the table. That is a literature check by web search, not a survey, so
`10c98c4b` stays a candidate. *Correction (22 Nov, morning):* B is prior art, the Δ-bijective algebras with their
dual operation (see the `10c98c4b` section above). The night's searches had looked only in the Latin-square
literature.

**Lean.** `lean/Duet/Cand1.lean` … `Cand10.lean` hold the smallest non-degenerate model of 10 candidates, with
proofs by `decide` that it satisfies the laws and refutes x·y = x, x·y = y, x∘y = x, x∘y = y, x·y = x∘y and
x·y = y∘x where they fail. The numbers follow the order in which certificates were made, not the rank: Cand1–5 are
the top 5 of the 62-candidate ranking, and Cand6–10 the new entries of the top 10. Each dossier names its file.
- Model JSON: `work/check/cand<i>_model.json`, written by `python -m soup.dossier lean-json --top 10` and checked by
  both evaluators.
- Generated with `python -m soup.lean_cert model --json ... --name Cand<i>`.
- `lean/check.sh` checks all 11 modules (with S10), and the axiom audit passes on 116 declarations: only `propext`,
  `Classical.choice` and `Quot.sound` appear.

The certificates are about finite models only. They show the theories are consistent and non-degenerate. They say
nothing about novelty.

Caveats:
- "Split" is proved by E, and "not split" has a finite certificate. "Not definitional" means no term of size ≤ 5
  matched on the models, or no matching term was proved in 30 s.
- The relabelling check uses the 10 named theories only. A theory can still be a known variety outside that list:
  rank 2 is one (left quasigroups with extra identities). The literature checks are web searches by the session,
  not a systematic survey.
- The 19 X1 candidates come from a run cut to 1.5 h (deviation 4). The ranking is the preregistered rubric applied
  to all 81. The first ranking, of the 62 (T5a section), is kept there as it was.
- Split theories and disguised one-operation varieties are a gap in the search's filters, not only in the ranking.
  The post hoc split scan over all T4 non-fragments shows the size of the gap (next table).

**Split scan of all T4 non-fragments (post hoc).** Command: `podman run -d -v "$PWD/work:/data" -e
SOUP_DATA=/data/t4-<arm> soup python -m soup.split --fragments 1 --jobs 1` (output
`work/t4-<arm>/split_nonfragments.json`). A first start crashed on laws with five variables, before any result was
written. Fixed, with a test, and rerun.

| T4 non-fragments | prior | noprior |
| --- | --- | --- |
| checked | 668 | 362 |
| split (E proof) | 35 | 4 |
| not split (certificate on 2 / 3 / 4 elements) | 532 (122 / 368 / 42) | 334 (32 / 233 / 69) |
| unknown (no certificate on 2–4 elements, and E derived no bridge from one-operation laws) | 101 | 24 |
| split share among the decided | 6.2% | 1.2% |
| split share, bounds with unknowns counted either way | 5.2–20.4% | 1.1–7.7% |

Among the decided, the prior arm has more split theories: 35/567 against 4/338, one-sided Fisher p = 1.2e-4. That
test is post hoc, not part of H1. 22 of the 35 split theories of the prior arm have a duality, and none of the 4 of
noprior does. A plausible reading: V(·) together with its mirror on ∘ is self-dual, so the duality prior rewards
it. Among the top 20 non-fragments by score, 1 is split in prior and 2 in noprior. T4's H1 counts fragments, so this
does not change it. It does mean that some of T4's non-fragments are not fusions at all.

## T5a: does an algebraist's profile separate named from random theories? (22 Nov 2026, night)

Preregistered (PREREGISTRATION.md, T5a). There are two analyses, because of deviation 3: the VM's OOM killer ended
3 profile children and 3 E runs during the first run, and the profile code counted a killed E run as "not
proved".

Commands:
- as run: `podman run -d -v "$PWD/work:/data" soup python -m soup.profile --set t3 --jobs 8`;
- rerun, fixed code, 4 jobs: `... python -m soup.profile --set t3 --name t3_rerun --jobs 4`;
- analysis: `python -m soup.profile --t5a` and `python -m soup.profile --t5a t3_rerun` (raw data
  `work/check/profile_t3*.json`, `work/check/t5a_report*.json`).

| feature | named (as run) | random (as run) | Holm p (as run) | named (rerun) | random (rerun) | Holm p (rerun) |
| --- | --- | --- | --- | --- | --- | --- |
| F1 Mal'cev-type term (primary, uncorrected) | 1/10 | 21/117 | 0.86 | 1/10 | 22/120 | 0.87 |
| F2 finite free algebra on 2 generators | 2/10 | 17/117 | 0.48 | 2/10 | 17/120 | 0.52 |
| **F3 convergent presentation** | **6/10** | **13/117** | **0.0022** | **6/10** | **13/120** | **0.0020** |
| F4 non-degenerate models on ≥ 3 sizes | 8/10 | 74/117 | 0.48 | 8/10 | 77/120 | 0.52 |

The rerun had no crashes and no prover errors, and there were no OOM kills during it (kernel log). Of the
127 × 4 feature values computed in both runs, one changed: a random theory's F4, from no to yes. The 3 theories that
crashed in the first run (random k = 2, 5 and 6) completed in the rerun.

- **H1 (primary, F1) is not supported.** Only the lattice has a Mal'cev-type term among the named theories: a
  majority term of size 4. 22 of the 120 random theories have one: 21 Mal'cev terms, 11 minority terms, and a few
  majority and Pixley terms. Several of these come from strong laws with very few models, such as
  group-like or affine structure over ℤ/2. Our named list has no congruence-permutable theory: the quasigroups in it
  are one-sided, and full quasigroups need three operations.
- **H3 (F3) is supported.** The named theories with a convergent presentation are the absorption pairs and the four
  one-sided quasigroups. Lattices, skew lattices and bisemilattices have none from E in 30 s. For lattices this is
  expected, since lattice theory has no finite convergent rewrite system (Freese, Ježek and Nation 1993).
  13 random theories have one.
- **H2 and H4 (F2, F4) are not supported.**
- Calibrated feature for the ranking (both analyses): **F3 only.**

Caveats:
- 10 named theories is a small sample. Several of them were picked for symmetry (T3), and F3 picks out exactly
  the absorption and quasigroup families.
- F3 depends on E's ordering and 30 s budget. "Not convergent" means none was found in that budget.
- The rerun was decided after the first result had been seen (deviation 3). The two agree on every test.

**Ranking (PREREGISTRATION.md, T5a "Use in ranking").** 62 candidates: the top 20 non-fragments by score from
each T4 arm and from the earlier runs, plus T1 and T2. No candidate is equivalent to a standard theory. 14 have F3;
they are ranked first, with ties broken by duality, then by the number of sizes with non-degenerate models, then
by score. Commands: `python -m soup.dossier candidates --sources t4-prior,t4-noprior,.`,
`python -m soup.profile --set candidates --jobs 2` (rerun from scratch after deviation 3),
`python -m soup.dossier rank` (table in `work/check/ranking.txt`).

| rank | source | key | laws | duality | non-degenerate models on 2/3/4/5 |
| --- | --- | --- | --- | --- | --- |
| 1 | earlier runs | `4dc33674` | x·(x·y) = y; (x∘y)∘y = x; x∘(x∘(x·y)) = x; ((x∘y)·y)·y = y | swap+opposite | 0 / 2 / 107 / ≥ 375 |
| 2 | T4 prior | `8a512957` | x·(y∘x) = y∘y; x·x = (y·x)∘y; x∘(x∘((y·z)∘x)) = x; ((x·(y∘z))·x)·x = x | swap+opposite | see dossier |
| 3 | T4 prior | `1ca933c1` | x·(y∘(x∘y)) = x; x∘(y·(x·y)) = x; x·((y∘x)∘y) = x; x∘((y·x)·y) = x; x·(((x·x)·y)∘z) = x; x∘(((x∘x)∘y)·z) = x | swap | see dossier |
| 4 | earlier runs | `3078949b` | x·(x·(y∘y)) = x; x·(y∘(x∘x)) = x; x∘(y·(x·x)) = x; x∘(x∘(y·y)) = x | yes | see dossier |
| 5 | earlier runs | `2dc27508` | x·(y·(x·x)) = x; ((x·x)·y)·x = x; (x∘y)·x = x·(z∘x) | yes | see dossier |

Dossiers: `work/dossiers/0N-<key>.md` (`python -m soup.dossier write --top 5`). They are candidates, not results.
The equivalence checks, the literature check and the Lean certificates are in the section above (post hoc). That
section also has the ranking after the 19 X1 candidates were added.

## T4: duality-prior search against a matched control (21–22 Nov 2026, night)

Preregistered (PREREGISTRATION.md, T4) and run unchanged at tag `t4-prereg` (`a5c60aa`):
- arms `prior` and `noprior`, each with its own data directory, under verifier V2, 2 searchers and 3 verifiers per
  arm;
- 14,400 s per arm, 21:20–01:20 UTC;
- seeds 201+ (prior) and 301+ (noprior);
- 4 workers crashed and were restarted by their supervisor, as preregistered. In prior, verifiers v1 (22:58) and
  v0 (00:09) exited on SIGABRT. In noprior, searcher s302 was killed by the VM's OOM killer at 00:00 (kernel log),
  and verifier v3 exited on SIGABRT at 00:11. Each verifier crash put its one claimed task back in the queue. No
  supervisor died. (A first version of this section said there were no crashes. The journals say otherwise.)

Commands:
- runs: `podman run -d --name soup-t4-<arm> -v "$PWD/work:/data" -e SOUP_DATA=/data/t4-<arm> -e SOUP_VERIFIER=V2
  soup python -m soup.stream.supervisor --arm <arm> --searchers 2 --verifiers 3 --seed0 <201|301> --budget 14400
  --run t4-<arm>`;
- fragment check: `podman run -d -v "$PWD/work:/data" -e SOUP_DATA=/data/t4-<arm> -e FRAG_JOBS=2 soup python -m
  soup.fragments`;
- analysis: `podman run --rm -v "$PWD/work:/data" soup python -m soup.t4_report` (raw output `work/t4_report.txt`,
  `work/t4_report.json`). The journals are in `work/t4-<arm>/journal/`.

| | prior | noprior |
| --- | --- | --- |
| theories verified | 1,050 | 441 |
| with positive score (H1 population) | 998 | 393 |
| fragments of a named theory | **330 (33.1%)** | **31 (7.9%)** |
| not fragments | 668 | 362 |
| undecided | 0 | 0 |
| fragments of lattices / skew lattices / bisemilattices | 329 / 27 / 17 | 30 / 1 / 0 |
| fragments of absorption pairs / idempotent left / right quasigroups | 16 / 11 / 10 | 1 / 1 / 0 |
| verified theories with a duality | 522 | 23 |
| claims still open at the end | 79 | 57 |
| structures added to the arm's corpus | 6,874 | 3,637 |

**H1 is supported.** Among verified theories with positive score, the share of fragments of a named theory is
higher with the prior: 330/998 against 31/393, one-sided Fisher p = 2.0e-25. No theory is undecided, so both bounds
equal the point estimate. The pilot (first session, different verifier, a control without the definitional filter)
had 64/97 against 6/59. The fragments are almost all lattice fragments: in the prior arm 295 of the 330 are
fragments of lattices only.

**Secondary: the top 10 non-fragment theories per arm, by V2 score.** None of the 20 is equivalent to another,
either up to the three dualities or by E proofs both ways. Every one is a candidate, not a result (rule 4).
The first run of `t4_report` ran 10 E processes at once, and the OOM killer ended 3 of them (deviation 3). It was
rerun with `T4R_JOBS=3`: E compared 34 pairs (those with equal model counts), none of the checks crashed, and the
table is unchanged. The first output is kept in `work/t4_report_asrun.txt`.

| # | arm | score | laws |
| --- | --- | --- | --- |
| 0 | prior | 2.167 | x·(y∘x) = y∘y; x·x = (y·x)∘y; x∘(x∘((y·z)∘x)) = x; ((x·(y∘z))·x)·x = x |
| 1 | prior | 1.773 | x·(x∘x) = x; x∘(x∘x) = x∘x; (x·y)·z = y·z; (x∘y)∘z = y∘z |
| 2 | prior | 1.722 | x·(x∘x) = x; (x·x)∘x = x; x∘((x·y)·z) = y∘y; (x∘(y∘z))·z = y·y |
| 3 | prior | 1.668 | x·(y∘(x∘y)) = x; x∘(y·(x·y)) = x; x·((y∘x)∘y) = x; x∘((y·x)·y) = x; x·(((x·x)·y)∘z) = x |
| 4 | prior | 1.659 | x·(x·x) = x; x·(y∘x) = y∘y; x·x = (y·x)∘y; x∘(x∘((y·z)∘x)) = x |
| 5 | prior | 1.599 | x·(y∘(x∘y)) = x; x∘((y·x)·z) = x; x∘(((x∘x)∘y)·z) = x |
| 6 | prior | 1.585 | x·(y∘x) = x·x; x∘(y·x) = x∘x; (x∘y)·x = x·x; (x·y)∘x = x∘x; x·(y·z) = y∘(x∘z); (x·y)·z = (x∘z)∘y |
| 7 | prior | 1.584 | the 5 laws of #3 and x∘(((x∘x)∘y)·z) = x (the swap closure of #3) |
| 8 | prior | 1.584 | x·(y∘(x∘y)) = x; x∘(y·(x·y)) = x; x·((y∘x)∘z) = x; x∘((y·x)·z) = x; x·(((x·x)·y)∘z) = x; x∘(((x∘x)∘y)·z) = x |
| 9 | prior | 1.555 | x·(x·x) = x; (x·x)·y = y·x; ((x∘(y·y))·z)∘y = y |
| 10 | noprior | 1.743 | x·(y∘(z·x)) = x; (x∘x)·(x·y) = x |
| 11 | noprior | 1.680 | (x∘x)·(y∘y) = y·x; (x·x)∘((y∘x)∘z) = x |
| 12 | noprior | 1.653 | x·y = y·x; x∘(y∘x) = x; (x·x)∘(x·y) = x |
| 13 | noprior | 1.575 | x·(x·x) = x; x∘(y·(z·x)) = x; (x∘x)∘(x·y) = y∘x |
| 14 | noprior | 1.521 | x·y = y·x; x·y = y∘(x·y); x·(y∘(z∘x)) = x |
| 15 | noprior | 1.519 | x·(x∘y) = x; (x·y)·x = (z∘y)·z |
| 16 | noprior | 1.513 | x·x = x∘x; x·(x∘x) = x; x∘(y·x) = x; (x·y)∘(y∘x) = y |
| 17 | noprior | 1.476 | x·x = x; (x∘x)·((y·x)·z) = x |
| 18 | noprior | 1.453 | x·x = x; x·(y∘x) = x; (x·y)·x = (z·x)∘x |
| 19 | noprior | 1.401 | x·y = y·x; x∘(y·(z∘x)) = x; (x·x)∘(x∘y) = x |

Caveats:
- **Throughput.** The prior arm verified 2.4 times as many theories in the same time. Its theories are often
  lattice-like, and E proves their claims quickly. The fragment share is per verified theory, so it inherits
  this, as it inherits the queue-top selection (preregistered limit).
- **Length.** The prior arm's theories are longer: 399 of its 998 have 5 or 6 laws, against 1 of 393. The duality
  closure adds the dual laws. **Post hoc**, not preregistered: the difference holds within each law count. Fragment
  shares are 30/121 against 4/111 at 2 laws (one-sided Fisher p = 2.1e-6), 77/250 against 12/194 at 3 laws
  (p = 1.5e-11) and 59/228 against 14/87 at 4 laws (p = 0.043).
- **What H1 shows.** The duality prior steers the search toward self-dual, lattice-type theories, i.e. toward
  structure people have already named. It does not show that the prior finds *unnamed* structure. The 668
  non-fragments of the prior arm, 353 of them with a duality, are where that question goes next (T5a profile,
  ranking and dossiers above).
- **Not every non-fragment is a fusion** (post hoc, section "Candidates after the ranking"). 35 of the prior arm's
  668 non-fragments and 4 of noprior's 362 are split into a ·-theory and a ∘-theory (E proof); 101 and 24 are
  undecided.
- Scores are V2 scores. The E proof length is an upper bound on proof length (preregistered limit).

## Stage-c sweep and second survivor round, clean track (21 Nov 2026, night)

Neither run uses any LLM input. The sweep finished all 32 results, with no crashes. Round 2 was stopped once its
remaining jobs were moot.

**Stage-c sweep.**
- Run: `podman run -d --name soup-sweepc -v "$PWD/work:/data" soup python -m soup.sweep_c --jobs 5`.
- Table: `podman run --rm -v "$PWD/work:/data:ro" soup python -m soup.sweep_c --summary` (raw data in
  `work/check/sweep_c.json`).
- What it does: `verify.stage_c` with `DEFAULTS` on every result that has an `unknown` or `open` claim (32
  results). E gets 2M processed clauses, and saturations are certified. Mace4 starts at the smallest size that stage
  a left unsearched and goes up to size 10. z3 gets a long run.
- Process: each result runs in its own child process. The first attempt used a shared process pool, and one dying
  worker took the pool down after 8 results (see Corrections).
- Done: 32 of 32 results (20 s to 5,095 s each, median 673 s; finished 21 Nov, about 20:55 UTC).

Survivor theories, compared with the offline LLM's refutations (table "Found offline with an LLM, machine-checked"
below):

| Theory | Claims | Our stage c | LLM's refutation | Reproduced? |
|---|---|---|---|---|
| S2 `45b1f0fb` | 1 | refuted, 7-element model | 7-element model | yes |
| S3 `4ec6760a` | 3 | refuted, 7 | 7 | yes |
| S4 `513de1ad` | 3 | refuted, 5 | 7 and 5 | yes |
| S8 `d25065b6` | 3 | refuted, 7 | 7 | yes |
| S5 `5e0dc923`, S6 `bbdd0d1c` | 3 + 3 | open; Mace4 complete to size 7 (S5 x∘x = x: 8), budget out | model on ℤ/13 | no: size 13 is beyond Mace4's 10 |
| S1 `00f017a6` | 3 | open; Mace4 complete to 9 | piecewise-linear model on ℤ | no, as expected: no finite model is known |
| S7 `cdf702b5` | 1 | open; Mace4 did not finish size 7 | infinite term model (hand proof) | no, as expected |
| S9 `e6403d7a`, S11 `f5321de4` | 3 + 3 | open; Mace4 complete to 7–8 (S9) and 10 (S11) | models on ℤ | no, as expected |
| S10 `f096b282`, S12 `f5e53602` | 3 + 3 | open; Mace4 complete to 5–6 only | none (left open) | — (round 2 below refutes 5 of the 6) |

Our stage c alone reproduces 10 of the LLM's 16 finite refutations. The other 6 (S5, S6) need 13 elements. The
models on ℤ and S7's term model are out of reach of finite search, which is what we expected. Every model found
here went into the shared corpus. On S10 and S12, Mace4 did not get past size 5–6 in its stage-c budget.

The other 20 results are not among the 12 survivor theories. Stage b's budget had left their claims undecided. Of
their 27 claims, E proves 25, each in 9–23 steps. The other 2, in `8fae253a`, are refuted by certified E
saturations.

**Second survivor round, clean track.**
- Run: `podman run -d --name soup-round2 -v "$PWD/work:/data" soup python -m soup.round2 clean --jobs 5 --secs
  1800`.
- Table: `podman run --rm -v "$PWD/work:/data:ro" soup python -m soup.round2 summary` (raw data in
  `work/check/round2_clean.json`).
- Budgets: 1,800 s per prover run; the first claim (S12 x·x = x) gets 3,600 s.
- Stopped after 22 of 32 jobs (`podman stop soup-round2`, 21 Nov, 19:58 UTC). The 10 unfinished jobs were all
  on S10 claims, which the model below settles.

| Claim | Provers (Twee, E `--auto-schedule`, Vampire casc, Vampire casc_sat) | Prover9, no weight limit | Mace4 | ℤ/n translation-invariant | Piecewise-linear on ℤ, window 3 |
|---|---|---|---|---|---|
| S12 x·x = x | nothing in 3,600 s each | stopped at 189 s: no proof, no saturation, 0 deletions | sizes 6–9: **size 6 complete, no model**; size 7 not finished in 7,200 s | none for n ≤ 8; n = 9–38 undecided (120 s per n) | none in 3,600 s |
| S12 x·x = x∘x | nothing in 1,800 s each | stopped at 134 s, same | size 6 complete, no model; size 7 not finished in 3,600 s | none for n ≤ 8; 9–23 undecided | none in 1,800 s |
| S10 x·x = x | Twee, E, Vampire casc: nothing; **Vampire casc_sat: CounterSatisfiable after 602 s (a finite model)** | stopped at 104 s, same | not run (stopped) | none for n ≤ 8; 9–23 undecided | not run (stopped) |
| S10 x·(x·x) = x | not run (stopped) | | | | |

**S10 and two S12 claims are refuted by a 10-element model.**
- Search: Vampire's casc_sat schedule (strategy `fmb+10_1_…`, finite model building at size 10). The round-2
  driver kept only the status line. A rerun with the full output (`work/check/s10_vampire_casc_sat.out`, 113 s in
  the successful strategy) printed the model.
- Check: `podman run --rm -v "$PWD/work:/data" soup python -m soup.round2 model --out
  /data/check/s10_vampire_casc_sat.out --key f096b282 --name s10`. It checks the tables with both of our evaluators
  (`core.law_vector` and the direct evaluation in `check_offline.check_finite`). Result: all five S10 axioms hold,
  x·x = x, x∘x = x and x·(x·x) = x fail, and the model is non-degenerate. The model is now in the corpus;
  tables in `work/check/s10_model.json` and in `tests/test_round2.py`.
- **Lean 4 certificate.** `lean/Duet/S10.lean` states the three non-implications over all types and proves them
  with `decide` on the tables. It checks with `-DwarningAsError=true`, and the axiom audit passes (8 declarations;
  propext, Classical.choice, Quot.sound only). Command: `podman run --rm -v "$PWD/lean:/src" -v "<compiled Mathlib
  v4.35.0 project>:/reuse:ro" soup-lean sh /src/check.sh`, 107 s.
- x·x = x fails at exactly one element: 0·0 = 0∘0 = 1.
- A model of S10 is a model of S12, so S12 ⇒ x·x = x and S12 ⇒ x∘x = x are refuted too. In this model x·x = x∘x
  holds by construction, so it says nothing about S12's third claim.
- **5 of the 6 claims the offline LLM left open are now refuted, by our own tools and without LLM input.** One
  claim is left: S12 ⇒ x·x = x∘x.
- Mace4 would not have found the model. It did not finish size 7 in 2 h, and round 2 gave it sizes 6–9 only. The
  ℤ/n family timed out at n = 9 and above. Vampire's FMB, which encodes each size as SAT, is the tool that worked.
  Stage c has no Vampire FMB; it is added after T4 as a new verifier config (V2 is preregistered).

**Follow-up runs (Block 1, 21 Nov, 20:02–21:21 UTC; outputs in `work/check/b1/`, jobs in `jobs.txt`).**
- *Do ETP Equations 437 and 3115 together imply x = x◇x?* Still open.
  - Vampire FMB from size 4 searched sizes 4–8 completely and found no model. Size 9 did not finish in 3,600 s.
    With ETP's own result for sizes 2–3, no magma with x ≠ x◇x on 8 or fewer elements satisfies both laws.
  - Vampire's casc_sat portfolio, whose FMB strategies went up to size 15, timed out at 3,600 s. Twee found no proof
    in 3,600 s.
  - E `--auto-schedule` was stopped by hand after 78 min with no result, so that T4 would run alone.
  - If the pair does imply x = x◇x, it is an order-4 one-operation synergy pair like E55 + E100, and it would
    settle S12's last claim only for x·y = x∘y.
- *Smallest S10 / S12 model with x·x ≠ x:* Vampire FMB from size 7 did not finish size 7 in 3,600 s, on either
  theory. The smallest such model still has 7–10 elements.

Caveats:
- Why Prover9 stopped early is not known, because its output was not kept. The likeliest cause is the 2,000 MB
  `max_megs` cap. None of those runs is a saturation.
- New since the LLM's round: S12 has no countermodel on 6 elements. Before, the complete search covered only sizes
  2–5. The smallest countermodel therefore has 7–10 elements; a Vampire FMB run from size 7 is going.

## T3: calibration, named vs random theories (21 Nov 2026)

Preregistered (PREREGISTRATION.md, T3, deviations 1 and 2). Run: `podman run -d --name soup-calib -v
"$PWD/work:/data" -e CALIB_JOBS=6 soup python -m soup.calib`, resumed after the crash: 69 results from the first
run, 61 from the resumed one, 130 in all. Analysis: `podman run --rm -v "$PWD/work:/data:ro" soup python -m
soup.calib_report` (raw output `work/check/calib_report_t3.txt`). Verifier V1 (z3 5.4.1, E 3.2.5).

**H1 (primary).** Named theories have a duality more often than random ones.

| | with a duality | without | one-sided Fisher p |
|---|---|---|---|
| named | 8 | 2 | |
| random, all 120 | 0 | 120 | 2.8 × 10⁻¹¹ |
| random, uniform-sampled 90 (k = 2, 3, 5) | 0 | 90 | 2.4 × 10⁻¹⁰ |

The two named theories without a duality are the idempotent left and right quasigroups: adding x·x = x
without x∘x = x breaks the swap symmetry of the one-sided quasigroup axioms. Two random theories crashed (one
at k = 5, one at k = 6), both at the 1-hour limit per theory. They count for H1, which is syntactic, and are
left out of H2. As preregistered, H1 is a sanity check of the duality prior: several named theories were
chosen because they are symmetric.

**H2 (descriptive).** Percentile of each named theory among random theories of the same size (ties count
half). The k = 6 null is model-first (deviation 1).

| theory | k | gain | max difficulty (z3) | max E steps | richness | score | dualities |
|---|---|---|---|---|---|---|---|
| lattice | 6 | 37.9 | 24.1 | 39.7 | 12.1 | 37.9 | swap |
| bisemilattice | 6 | 24.1 | 17.2 | 15.5 | 75.9 | 37.9 | all three |
| skew lattice | 6 | 37.9 | 24.1 | 39.7 | 34.5 | 41.4 | all three |
| dimonoid | 5 | 10.3 | 10.3 | 10.3 | 81.0 | 10.3 | swap+opposite |
| idempotent left quasigroup | 3 | 36.7 | 43.3 | 38.3 | 28.3 | 36.7 | – |
| idempotent right quasigroup | 3 | 40.0 | 26.7 | 38.3 | 28.3 | 36.7 | – |
| absorption pair | 2 | 50.0 | 50.0 | 61.7 | 70.0 | 50.0 | swap |
| right absorption pair | 2 | 50.0 | 50.0 | 50.0 | 70.0 | 50.0 | swap |
| left quasigroup | 2 | 25.0 | 25.0 | 25.0 | 46.7 | 25.0 | swap |
| right quasigroup | 2 | 25.0 | 25.0 | 25.0 | 46.7 | 25.0 | swap |

Every named theory sits between the 10th and 82nd percentile on every measure. On gain, difficulty and score
all ten are at or below the median of the random theories of their size. So the synergy score does not
prefer the theories people named, and if anything ranks them low; symmetry separates them, synergy does not.
That fits the first-session expectation (9th–91st percentile) and the design of T4, which tests the duality
prior, not the score, as the route to interesting theories. Random theories with positive score: 15/30 (k = 2),
24/30 (k = 3), 26/30 (k = 5), 27/30 (k = 6).

Caveats: the shared corpus grew during the run (stream runs before it, the calibration's own models during
it), so later theories saw more structures. The first 69 theories ran without memory caps. The scores are V1,
with the z3 budget-cap artifact (see Corrections); the percentile ranks of difficulty and score could move
under V2.

## Literature check (21 Nov 2026, evening)

Web and arXiv search for 2024–2026 work, done by a subagent. Each arXiv entry below was confirmed through the arXiv API
(title, authors, date); entries marked *[not verified]* rest on the subagent's reading only.

| Work | What it means here |
|---|---|
| Bolan et al., *The Equational Theories Project*, arXiv:2512.07087 (Dec 2025) | The one-operation census we build on; its countermodel methods (linear, translation-invariant, greedy) are ours for the hard cases. No two-operation census found. |
| Janota, Rawson, Schulz, *Saturations as Explicit Models in Equational Theories*, arXiv:2602.16324 (Feb 2026) | **Our A–D certificate method is published**: a saturated unit-equality clause set read as a convergent rewrite system, i.e. an explicit, possibly infinite model, emitted from Vampire and E and checkable by certified tools. `soup.confluence` is an independent implementation. Cite it; cross-checking with certified tools is open. |
| Le Floch, *Implication semilattice of 990 quadratic quasigroup equational laws*, arXiv:2603.29909 (Mar 2026) | All implications between *conjunctions* of 990 laws in three operations: the closest published analogue of a census of theories. |
| Kondylidou, Blanchette, Heule, *Tao's Equational Proof Challenge Accepted*, arXiv:2605.21200 (May 2026) | Proof minimisation (Krympa) cuts ETP proofs from 62 to 20 and 151 to 10 steps. Raw proof length (V2 difficulty) is an upper bound; noted in the T4 preregistration before the run. |
| Zhao, Wu, Yang, Miao, *Trace-Tree Magmas*, arXiv:2609.05690 (Sep 2026) | 28 order-5 Austin laws with Lean-certified infinite models; relevant to T7 (order 5). |
| Berlioz, Melliès, *The Latent Space of Equational Theories*, arXiv:2601.20759 (Jan 2026) | Laws represented by their behaviour on finite magmas, as in our law × structure matrix. |
| Lean Zulip, ETP stream, topic "Search space for (EqX ∧ EqY) → EqZ" (Oct 2024 – Sep 2025; archive at https://leanprover-community.github.io/archive/stream/458659-Equational/, read 21 Nov 2026, night) | **Conjunctions of two ETP laws, the question of our census.** Tsyrklevich estimates about 785M (X, Y, Z) cases left after transitivity. In Sep 2025 Le Floch lists all conjunctions of low-order laws: 59 classes, closed under conjunction (his pairs use Equations 2–43; Equations 1–46 have order ≤ 2). Tao asks for the data in the ETP repository. No order-3 pair appears, so E55 + E100 (order 3) is not covered there. A forum thread, not a publication. |
| SAIR EQT2 solvers (arXiv:2609.00706, 2610.26467), ALPS (arXiv:2608.15979), *Learning to Disprove* (arXiv:2603.19514) | LLM-assisted work on equational implication; all keep the LLM out of verification, as our rule 6 does. |
| Leech, *Noncommutative Lattices* (2020), Thm 1.3.4, citing Laslo–Cozac 1998 *[not verified]* | Which order-2 absorption pairs force idempotence is classified; our absorption calibration is a special case: reproduced, not found. |
| CASC-J13 (2026) rules and TPTP v10.0.0 *[not verified]* | Unit-equality division takes provable problems only; infinite-only non-implications (A–D, S1, S9, S11) fit the FNT division, which accepts saturations. Submission is by contacting the TPTP developers. |

Checked by us against the ETP data (`data/equations.txt`, `2024-11-10-outcomes.json`) and our evaluator:

- With x·y = x∘y, S12 collapses to E437 and E3115. Each has non-idempotent models (2 on 2 elements, 48 on
  3), but no 2- or 3-element non-idempotent magma satisfies both. ETP: neither implies E3 (x = x◇x), and
  neither implies the other.
- S5/S6 collapses to E43 ∧ E48, and E48 alone implies E3. So any countermodel needs · ≠ ∘, as the 13-element
  one has. T1's second law collapses to E2927, which alone implies E3.
- **T2 collapses to E55 ∧ E100.** ETP: neither alone implies E3. Together they do: E proves it in 10 steps,
  Twee in 3. E100 alone saturates; for E55 alone E gives up, and ETP records the non-implication. This is a
  one-operation pair with synergy, which ETP does not test because it does not consider conjunctions. Not
  found in the literature; the search was by formula strings, which is weak evidence, so this is not a claim
  of novelty.

No prior appearance was found for S12, S5/S6, T1 or T2 (formula-string search; weak evidence).
Prover versions: E 3.2.5 is the latest official release, but development tags reach E 3.5.11, and CASC-J13
ran E 3.5.1; Vampire 5.1.0, Twee 2.7.1 and LADR-2026-8A are current.

## Found offline with an LLM, machine-checked (21 Nov 2026, evening)

An external LLM got `prompts/survivors.md` (the 32 survivor claims) outside the repository. Its bundle lives in
`$OFFLINE/survivors-external01-2026-11-21/` (a scratch directory outside the repository). Nothing from it entered `work/results`, the corpus or the
archive. Check: `tar -C <bundle> -cf - S*.md | podman run -i --rm -v "$PWD/work:/data:ro" soup python -m
soup.check_offline > <bundle>/check.jsonl`. Axioms and claims come from our `work/results`; only the
tables, the hand-transcribed ℤ formulas and the lemma statements come from the bundle.

| Theory (key) | Claims | Evidence | Our check |
|---|---|---|---|
| S2 `45b1f0fb` | 1 refuted | finite model, 7 elements | `law_vector` + direct evaluation: axioms hold, claim fails, non-degenerate |
| S3 `4ec6760a` | 3 refuted | finite model, 7 | same |
| S4 `513de1ad` | 3 refuted | finite models, 7 and 5 | same (our stage a had left sizes 5–6 unsearched) |
| S5 `5e0dc923`, S6 `bbdd0d1c` | 3 + 3 refuted | finite model on ℤ/13, translation-invariant, commutative | same |
| S8 `d25065b6` | 3 refuted | finite model, 7 | same |
| S1 `00f017a6`, S9 `e6403d7a` | 3 + 3 refuted | piecewise-linear model on ℤ | every axiom proved for all integers by z3 (linear integer arithmetic); claims fail at 0 |
| S11 `f5321de4` | 3 refuted | max/min off the diagonal, x·x = x+1, x∘x = x−1, on ℤ | same |
| S7 `cdf702b5` | 1 refuted | infinite term model with an "anchor" map | **not certified**: hand proof (read, checked step by step), reimplemented from the prose and sampled (≈ 900 elements, 200k axiom triples, 0 failures) |
| S10 `f096b282`, S12 `f5e53602` | 6 open | lemma chains only | E proves all 39 lemmas of the bundle from the axioms |

So 25 of the 32 survivor claims are refuted with a machine check (16 by finite models, 9 by models on ℤ
proved over ℤ). One more (S7) is refuted by a hand proof that has been sampled but not certified. Six remain
open. *Update (21 Nov, night):* our own round 2, with no LLM input, refutes five of the six with a 10-element
model of S10 found by Vampire's finite model builder (section above). The only claim still open is S12 ⇒ x·x = x∘x.
Counting both sources: 30 of 32 refuted with a machine check, S7 by a sampled hand proof, 1 open. Caveat: the 32 come from the three short test runs above (`test10`, `fix5`, `e10`: about 25 minutes of
streaming, 354 verified theories) and only from queue-top theories, a small, selected sample. The share of
false claims describes this sample, not the search. The finite-model share says something about our pipeline: 16 survivors had countermodels of size 5, 7
or 13 that our search never reached (see the corrections below).

## Corrections and fixes (21 Nov 2026, evening)

Found while reviewing the code and the offline results; each fix has a test (`tests/test_fixes.py`,
`tests/test_check_offline.py`, `tests/test_families.py`; 40 + 1 tests pass in the container).

- **Survivor coverage was overstated.** z3 ran out of budget at size 6 (or 5 and 6) in stage a for 9 of the
  12 survivor theories, and none reached stage c, so Mace4 never ran on them. Stage c also started Mace4 at 7
  regardless. Now it starts at the smallest size stage a left unsearched.
- **OOM kills.** The kernel log of the Podman VM shows 4 Vampire processes of the open-claim sweep killed at
  2–4.4 GB, and the T3 worker killed at 5.9 GB. E, Vampire, Twee, Prover9 and Mace4 now run under a 2 GB cap
  (`SOUP_PROVER_MEMORY_MB`). Prover9's and Mace4's own defaults (200 / 500 MB) had silently limited earlier runs.
- **Prover9 "saturation" was unsound.** `prove_prover9` reported every empty set of support as
  countersatisfiable, but Prover9 deletes clauses over its default `max_weight`. On S12 it deleted 8,216 of
  8,561 generated clauses. An empty sos now counts only with zero deletions. A–D re-checked: zero deletions,
  so the "Prover9 agrees on A–D" line below stands.
- **Stage b took E saturations without a certificate**, although the paper says every refutation carries one.
  DEFAULTS now runs `soup.confluence` on each saturation (`certificate` field; status
  `false (E saturation, uncertified)` when the check fails). T3 keeps the frozen verifier `V1`, without it.
- **Score artifact.** A claim that E proved but z3 did not got difficulty = log of z3's budget. 14 of 983
  proved claims; the top two leaderboard theories (`d5584040`, `17b2a537`) score entirely from it. T4 uses
  the preregistered V2 (difficulty = E proof steps / 10). Post-hoc comparison: `python -m soup.rescore`
  (641 older proved claims have no E steps and get the floor, so it is only indicative).
- **The first stage-c sweep repeated a pitfall already on record.** It used one `ProcessPoolExecutor`. One
  worker died (the kernel log shows no OOM kill), and the broken pool turned the other 24 jobs into errors after 8
  results. `sweep_c` now runs one child process per result, records a crash without touching the result file, and
  skips results already swept on a rerun (commit `6372256`). The 8 finished records are kept.
- **Mutation bug.** The remove-a-law mutation removed a random number of laws, not one.
- **Fragment check was biased toward "not a fragment"** (z3 giving up counted as invalid). It is now
  three-valued (valid / invalid / undecided) over all 10 named theories of T3.
- **ETP lookup** (data/2024-11-10-outcomes.json of the Equational Theories Project). The one-operation
  specialisation of S12 (x·y = x∘y) has the laws Equation 437, `x = x◇(y◇(y◇(x◇y)))`, and Equation 3115,
  `x = (((y◇x)◇y)◇y)◇x`. ETP: neither implies x = x◇x, and neither implies the other. ETP says nothing about
  the pair, so the one-operation route to an S12 countermodel stays open.

## Open-claim sweep (21 Nov 2026)

All 59 claims open in `work/results/` (52 of them verified before E was in the pipeline), re-checked with
`python -m soup.sweep_open` (E 2M processed clauses / 300 s; saturations certified by `soup.confluence`;
Vampire cross-check), then Vampire 300 s with `-sa discount` and with the default strategy on the rest.

| Outcome | Claims |
| --- | --- |
| proved (E and Vampire) | 25 |
| refuted, certified convergent system (infinite countermodel), Vampire agrees | 2 |
| open after E and Vampire | 32 (12 theories), listed in `work/journal/survivors.md` |

Two E runs were labelled "error": E's CPU limit (exit 8) under load, now reported as unknown.
Every one of the 32 open claims is one of x·x = x, x∘x = x, x·x = x∘x, x·(x·x) = x, x·(x∘y) = x, x·(y·x) = x.

## T2: E 3.2.5 (21 Nov 2026)

E 3.2.5 built from the sha256-pinned source tarball (3.5.x tags were 1–12 days old: not pinned).
Command: `podman run --rm -v "$PWD/work:/data" soup python -m soup.t2_smoke --jobs 10 --cpu 300 --limit 2000000`
(output `work/check/t2_smoke_e.json`). E options: `--auto`, processed-clause budget, proof object.

| Case | E result | proof steps | processed clauses | z3 (earlier) |
| --- | --- | --- | --- | --- |
| absorption ⇒ x·x = x | proved | 9 | 7 | effort 494 |
| T1 ⇒ x·x = x / x·x = x∘x | proved | 10 / 11 | 5 / 8 | 134,513 |
| T2 ⇒ x·x = x / x·x = x∘x | proved | 11 / 11 | 6 / 8 | 11,827 |
| McKenzie basis ⇒ x·y = y·x | proved | 21 | 83 | 8.5M (328 s) |
| A, B, C, D ⇒ x·x = x | CounterSatisfiable | – | 6, 6, 10, 4 | unknown |

- Soundness control: 22 claims refuted earlier by finite countermodels: E proves 0, saturates 5.
- Cross-check on 641 claims z3 proved: E proves 640 (misses one `x · x = x ∘ x` at 50k clauses).
  Spearman z3 effort vs E proof steps 0.365, vs E processed clauses 0.338; E steps median 11, max 27.
- **A–D refuted.** Same verdict under `--auto`, `-tLPO4 -Garity -Ginvfreq`, `-tLPO4 -Gunary_first`.
  Independent certificate (`python -m soup.confluence`, output `work/check/confluence_AD.txt`): E's saturated
  sets give convergent systems of 5, 5, 5, 3 rules (10, 10, 11, 5 critical pairs, all joinable), axioms
  joinable, x·x and x with different normal forms. Countermodels are infinite (term algebra modulo the
  rules). Caveat: one prover found the rule sets; correctness rests on the checker (tested in
  `tests/test_confluence.py`).
- **Second prover agrees.** Vampire 5.1.0 (source build, commit 7b2f410e, without z3): A–D CounterSatisfiable
  under the default strategy and under `-sa discount`; absorption, T1, T2 and McKenzie proved
  (`tests/test_named.py::test_vampire_agrees_with_e_on_reference_and_A_to_D`).
- **Third prover agrees.** Prover9 2026-8A: A–D end with an empty set of support (saturation) in ≈ 0.01 s each
  (`work/check/mace4_AD.txt`).
- Mace4 2026-8A on A–D, goal x·x = x, 900 s each, 4 in parallel: no countermodel; sizes fully searched
  7 (A), 8 (B), 6 (C), 8 (D) (`work/check/mace4_AD_sizes.txt`). Not better than the earlier z3 grounding
  (8 for A, 7 for C). Consistent with the countermodels being infinite. Stage c now runs Mace4 on sizes 7–10
  for 300 s; in practice expect it to finish size 7 only on 3-law theories like these.
- Correction: Prover9/Mace4 is maintained (github.com/AlgorithmicTruth/Prover9, release LADR-2026-8A,
  August 2026, GPL-2.0). My earlier note that LADR was unmaintained since 2009 was wrong.
- E is now in the verifier: stage b runs E first (saturation ⇒ claim false), stage c runs E before the
  size-7/8 model search. Difficulty is still z3 effort; E steps are recorded as `e_steps`.

## T1 follow-up runs (21 Nov 2026)

| Run | Change | Verified | Notes |
| --- | --- | --- | --- |
| `fix5` (300 s) | push gate, z3 memory cap 1.5 GB, grounding cap 60k, interruptible stop | 6 | every verifier took a stage-c task (5+ min each): fixed by capping stage c to verifiers/4 |
| `e10` (600 s) | + E in stages b/c, stage-c cap, retire only idle verifiers | 119 (115 positive) | 8 claims refuted by E saturation in stage b; shutdown 10 s after budget (was 135 s); peak total PSS 9.0 GB, max one process 1.7 GB |

Commands: `podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 300 --run fix5 --rebalance 60`,
`... --budget 600 --run e10`. Top scores are all theories forcing x·x = x, x∘x = x, x·x = x∘x: the score
saturates on idempotence.

## T1: 10-minute streaming test run (21 Nov 2026, run `test10`)

Command: `podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 600 --run test10`
(3 searchers seeds 101–103, arm prior, 8 verifiers, 11 cores, z3 5.4.1). Sources: `work/journal/journal.md`,
`work/logs/stats.jsonl` (37 lines for this run), `work/check/leaderboard_test10.md`.

| Quantity | Value |
| --- | --- |
| Wall time | 735 s (budget 600 s + 135 s waiting for verifiers stuck inside z3 calls, then SIGKILL) |
| Theories verified (stages a+b) | 231 (218 positive score); 1 finished stage c, 26 waiting in the stage-c lane |
| Claims still open after b | 50 (in 28 theories) |
| Surrogate evaluations | 851,670 (≈ 800/s per searcher) |
| Structures added to the corpus | 1,897 |
| Pushed to the queue / dropped by the 1,500 cap | 6,400 seen / 4,898 dropped |
| Rebalancing | one move (searcher → verifier at 2:11); then 0 competitive items, but the stage-c backlog blocked the move back |
| Top score | 2.448: x·(y∘y) = y·x & (x∘(y∘z))·y = y (forces x·x = x, x∘x = x, x·x = x∘x); not yet checked against named theories |

Memory per process (stats line at 308 s, from `/proc/<pid>/smaps_rollup` and `/proc/<pid>/smaps`):

| Process | RSS MB | PSS MB | private MB | matrix RSS / PSS MB |
| --- | --- | --- | --- | --- |
| searcher | 529–533 | 291–295 | 261–265 | 213 / 25 |
| verifier (typical) | 600–980 | 330–710 | 290–680 | 211 / 24 |
| verifier v6 (stage b) | 2,341 | 2,069 | 2,035 | 212 / 25 |

The mmapped matrices (213 MB) are shared: each process is charged ≈ 25 MB of them. A searcher now costs
≈ 290 MB PSS against ≈ 750 MB per process before T0. Total PSS peaked at ≈ 7.2 GB of the 12 GB VM.

Caveats and problems found:
- Searchers produce candidates ~30× faster than verifiers consume them; priority order plus the cap means
  low-cheap-score theories are never verified (a selection effect to state in T4).
- Groundings at size 6 for laws with 5–6 variables can take > 2 GB in one verifier. Needs a memory guard
  before an 11-process multi-hour run.
- One stage-c verifier is not enough (1 done in 10 min).
- Difficulty is still z3 effort; prover proof length comes with T2.

## T0: repo hygiene (21 Nov 2026)

| Check | Result | Command |
| --- | --- | --- |
| pytest in the container | 17 passed in 4.6 s | `podman run --rm -v "$PWD/work:/data" soup bash run.sh test -v` (output: `work/check/pytest.txt`) |
| Matrix rebuild with the refactored code vs the original code | byte-identical: meta.pkl `b86e9c11…0261`, M_law_major `e5b0ae54…8d52`, M_probe_major `72b1057d…b3a` | `bash run.sh matrix`, then `cd work && shasum -a 256 -c ../tests/matrix.sha256` |
| Law order vs the cloud results | all verified theories in `loopdual_31.pkl` and `loop_3.pkl` render the same law strings | `tests/test_matrix.py` |
| z3 on aarch64 | z3-solver 5.4.1.0 wheel exists; absorption effort = 494, same as the cloud | `tests/test_named.py` |
| Matrix build time | 155 s on 11 cores (was 8.5 min on 2) | `bash run.sh matrix` |

Caveat: the reference hashes come from the original code run on this Mac (`work/check/orig`), because no
`meta.pkl` was kept from the cloud. Agreement with the cloud is checked through law order only.
