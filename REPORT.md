# REPORT

Newest first. Every number has the command that produced it. Times in the journal are UTC.

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
