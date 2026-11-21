# REPORT

Newest first. Every number has the command that produced it. Times in the journal are UTC.

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
