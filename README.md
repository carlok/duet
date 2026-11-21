# duet: search for synergy between two binary operations (Python package `soup`)

> **Work in progress.** This is a research log, not a finished result: no theory found so far is claimed to be
> new, the paper in `tex/` is a draft, and `REPORT.md` states the caveats next to every number. Open problems
> that anyone can attack are listed [below](#open-problems).

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
- **Calibration (T3, preregistered).** Named theories have a syntactic duality and random ones don't: 8 of 10
  vs 0 of 120 (one-sided Fisher p = 2.8 × 10⁻¹¹). On gain, difficulty and score all ten named theories sit at
  or below the median of random theories of their size. Symmetry separates them; the synergy score does not.
- **Implications that finite search cannot settle.** Four pilot implications (A–D) are false, and their
  countermodels are necessarily infinite. E, Vampire and Prover9 all saturate, and our own check of the
  saturations (`soup/confluence.py`) certifies convergent rewrite systems.
- **Survivor claims.** 32 claims resisted E and Vampire. They are a small, selected sample: three short test
  runs (about 25 minutes, 354 verified theories), queue-top theories only. An external LLM worked on them
  outside the pipeline, and we machine-checked its answers (`soup/check_offline.py`):
  - 25 are refuted: 16 by finite models of size 5, 7 or 13, and 9 by models on ℤ proved over ℤ by z3;
  - 1 more (S7) rests on a hand proof that has been sampled but not certified;
  - 6 were left open, in two theories (S10, S12).
  - Our own second round, with no LLM input, refutes 5 of those 6. Vampire's finite model builder found a
    10-element model of S10 in which `x·x = x` fails at one element. Both of our evaluators check it, and it is
    also a model of S12. **One claim is still open: S12 ⇒ `x·x = x∘x`.**
  - Our own stage c, with no LLM input, independently finds 10 of the 16 finite refutations (S2, S3, S4, S8; sizes
    5 and 7). The other 6 need 13 elements, more than Mace4's 10 (all 32 results swept).
- **Synergy inside one operation.** Setting `x·y = x∘y` in the theory T2 gives ETP Equations 55,
  `x = x◇(y◇(y◇x))`, and 100, `x = x◇((x◇x)◇y)`. By the ETP data neither implies `x = x◇x`, but together
  they do (E: 10 steps, Twee: 3). ETP's implication graph does not cover conjunctions. A Lean Zulip thread has
  all conjunctions of the order ≤ 2 laws, but this pair is order 3, and we found no source for it. It is recorded
  as an observation (`REPORT.md`, literature check). A separate session is building the census of such pairs.
- **Not yet:** no theory found so far is new. The old score saturates on idempotence, and its top two
  theories were an artifact of z3's budget cap. T4 tests a corrected score (preregistered).

## Open problems

Each of these defeated E, Vampire, Twee (where run), Prover9 and finite-model search in our budgets. A proof, a
finite countermodel, or an infinite one with a checkable construction settles it. The budgets are in `REPORT.md`.

- **S12.** Do the four laws
  `x·(y∘(y∘(x∘y))) = x`, `x∘(y·(y·(x·y))) = x`, `(((x∘y)∘x)∘x)·y = y`, `(((x·y)·x)·x)∘y = y`
  imply `x·x = x∘x`? They do not imply `x·x = x`: a 10-element model refutes that (`tests/test_round2.py`). That
  model satisfies `x·x = x∘x`, so it does not answer this question. No model on 2–6 elements has `x·x ≠ x`
  (complete search), so the smallest one has 7–10 elements. With `x·y = x∘y` the laws become ETP Equations 437 and
  3115. Each alone has non-idempotent models, but no 2- or 3-element non-idempotent magma satisfies both. Whether
  the two together imply `x = x◇x` is open; a run is going.
- **The infinite-only non-implications** (A–D in the paper, and S1, S9, S11 in `REPORT.md`) are candidates
  for the TPTP library's non-theorem problems. Their countermodels are certified but necessarily infinite.

## License

Code: MIT (`LICENSE`). Text, paper and tables (`REPORT.md`, `PREREGISTRATION.md`, `tex/`): CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/).

## Status (21 Nov 2026, night)

Running (detached containers; `podman ps`; logs with `podman logs <name>`):
- **T4**, started 21 Nov 21:19 UTC at tag `t4-prereg` (commit `a5c60aa`), 4 h. `soup-t4-prior` and `soup-t4-noprior`:
  `SOUP_DATA=/data/t4-<arm>`, `SOUP_VERIFIER=V2`, `--searchers 2 --verifiers 3`, seeds 201 / 301, `--budget 14400`.
  Journals: `work/t4-<arm>/journal/journal.md`.
- The census session's `census-g3b` (2 CPUs, on its own branch).

Finished tonight:
- the stage-c sweep (32 of 32; `python -m soup.sweep_c --summary`);
- round 2's clean track (stopped after 22 of 32 jobs once the S10 model made the rest moot;
  `python -m soup.round2 summary`; the model is checked with `python -m soup.round2 model`);
- the Block 1 follow-up jobs (`work/check/b1/`);
- the first Lean certificate (`lean/`).

Next, in order (plan: T4, then T5a calibration, profiles, exploratory run, dossiers):
1. After T4: the preregistered analysis (`fragments` per arm, `t4_report`).
2. T5a: `python -m soup.profile --set t3 --jobs 8`, then `python -m soup.profile --t5a`.
3. The assisted round-2 track, after T4: `tar -C ~/tmp/duet-offline/survivors-external01-2026-11-21 -cf -
   S10.md S12.md | podman run -i --rm -v "$PWD/work:/data:ro" soup python -m soup.round2 assisted >
   ~/tmp/duet-offline/survivors-external01-2026-11-21/round2_assisted.jsonl`. It uses the LLM's lemmas only after E proves each one.
4. T5 (look hard at the top non-fragment theories), T6 (remaining open claims), T7 (Lean certificates,
   order-5 laws). A separate session is building a census of one-operation synergy pairs on ETP data
   (`work/census/`). Its next measure: which pairs that force idempotence keep a non-trivial model, and which
   collapse to x = y.

Task state: T0 (repo hygiene), T1 (streaming system), T2 (provers) and T3 (calibration) are done. T4 is
preregistered; T5–T7 have not started.

Offline LLM work follows `prompts/README.md`: bundles live in `~/tmp/duet-offline/`, never in the repository or
`work/`, and count only after `soup.check_offline` (in their own REPORT table).
