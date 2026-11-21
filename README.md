# duet: search for synergy between two binary operations (Python package `soup`)

An open-ended search over small equational theories in two binary operations, `x · y` and `x ∘ y`. Laws go up to
order 4: 71,369 laws up to renaming and side swap, 61,983 of them *bridges* that mix both operations. The search
looks for theories whose laws together imply laws that no single law implies (*synergy*; the reference case is the
lattice absorption pair, which forces both operations to be idempotent). Every claim goes through finite-model
search and theorem provers before it is reported.

Everything runs inside Podman; nothing is installed on the Mac. Data stays in `work/` (mounted at `/data`); the
code is in the `soup/` package, copied into the image.

    cd <this repository>
    podman build -t soup .
    podman run --rm -v "$PWD/work:/data" soup bash run.sh test            # builds the matrix first if missing
    podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 3600

The image carries z3 5.4.1 and five provers built from pinned sources: E 3.2.5, Vampire 5.1.0, Prover9/Mace4
LADR-2026-8A and Twee 2.7.1. The streaming search starts search and verifier processes (rebalanced by queue
length) and writes:

- `work/journal/journal.md`: what happened, in order (runs, notable verified theories, rebalancing, status)
- `work/journal/leaderboard.md`: top verified theories, rewritten every 15 s
- `work/logs/stats.jsonl`: one line per 15 s (queue, results, corpus, memory per process)
- `work/results/<key>.json`: one verified theory per file; `work/corpus/`: every structure found

`CLAUDE.md` has the project rules, code map and task list; `REPORT.md` has every number with the command
that produced it; `PREREGISTRATION.md` has the hypotheses, fixed before each scaled run.

## Results so far

- **Rediscovery.** The search finds lattice fragments, and two of the four laws of McKenzie's 1970 lattice basis.
- **Calibration.** Named theories have a syntactic duality and random ones don't: 8 of 10 vs 0 of 59 so far
  (T3, still running). Proof difficulty does not separate named from random theories.
- **Implications that finite search cannot settle.** Four pilot implications (A–D) are false, and their
  countermodels are necessarily infinite. E, Vampire and Prover9 all saturate, and our own check of the
  saturations (`soup/confluence.py`) certifies convergent rewrite systems.
- **Survivor claims.** 32 claims resisted E and Vampire. An external LLM worked on them outside the pipeline,
  and we machine-checked its answers (`soup/check_offline.py`):
  - 25 are refuted: 16 by finite models of size 5, 7 or 13, and 9 by models on ℤ proved over ℤ by z3;
  - 1 more (S7) rests on a hand proof that has been sampled but not certified;
  - 6 remain open, in two theories (S10, S12). A second round with our own tools is running.
- **Not yet:** no theory found so far is new. The old score saturates on idempotence, and its top two
  theories were an artifact of z3's budget cap. T4 tests a corrected score (preregistered).

## Status (21 Nov 2026, evening)

Running (detached containers; `podman ps`; logs with `podman logs <name>`):
- `soup-calib`: the T3 calibration, resumed after an OOM crash (PREREGISTRATION.md, deviation 2). Output
  `work/calib_t3.json`, 130 entries when done. Then: `podman run --rm -v "$PWD/work:/data" soup python -m
  soup.calib_report` and the T3 table in REPORT.md.
- `soup-round2`: the second survivor round on S10/S12, clean track (no LLM input; Twee, Vampire portfolios, E
  auto-schedule, Prover9 with no weight limit, Mace4, ℤ/n and piecewise-ℤ model families). Output
  `work/check/round2_clean.json`.

Next, in order:
1. T3 table in REPORT.md and the paper's calibration paragraph.
2. Stage-c sweep over every open claim: `python -m soup.sweep_c --jobs 6` (our pipeline; writes `results/`).
3. T4 (approved): `python -m soup.t4_setup`, then two supervisors at once with
   `SOUP_DATA=/data/t4-prior` / `t4-noprior`, `SOUP_VERIFIER=V2`, `--arm prior|noprior`, `--searchers 2
   --verifiers 3`, `--seed0 201|301`, `--budget 14400`. Start it once the round-2 container has finished, so the
   two do not exceed the VM's 12 GB.
4. The assisted round-2 track, after T4: `tar -C ~/tmp/duet-offline/survivors-external01-2026-11-21 -cf -
   S10.md S12.md | podman run -i --rm -v "$PWD/work:/data:ro" soup python -m soup.round2 assisted >
   ~/tmp/duet-offline/survivors-external01-2026-11-21/round2_assisted.jsonl`. It uses the LLM's lemmas only after E proves each one.
5. T5 (look hard at the top non-fragment theories), T6 (remaining open claims), T7 (Lean certificates,
   order-5 laws).

Task state: T0 (repo hygiene), T1 (streaming system) and T2 (provers) are done. T3 is running and T4 is
preregistered; T5–T7 have not started.

Offline LLM work follows `prompts/README.md`: bundles live in `~/tmp/duet-offline/`, never in the repository or
`work/`, and count only after `soup.check_offline` (in their own REPORT table).
