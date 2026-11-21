# Handoff (21 Nov 2026, end of the first Mac session)

Read `CLAUDE.md` first, then this file, then `REPORT.md` (newest first) and `PREREGISTRATION.md`.
Remote: github.com/carlok/duet (private). Local folder and Python package are still called `soup`.

## Running right now

- **T3 calibration**, detached container `soup-calib` (started ~10:40 UTC 21 Nov):
  `podman run -d --rm --name soup-calib -v "$PWD/work:/data" soup python -m soup.calib`.
  10 named + 120 random theories, 10 at a time; results stream into `work/calib_t3.json`.
  Check: `podman ps | grep calib`; `python3 -c "import json;print(len(json.load(open('work/calib_t3.json'))))"` (130 = done).
  When done: `podman run --rm -v "$PWD/work:/data" soup python -m soup.calib_report` and write a T3 table in
  `REPORT.md` (Fisher on all random theories and on the uniform ones only: see PREREGISTRATION.md, deviation 1).
  Stop rule: each theory verified once, no reruns, no exclusions.

## State of the tasks

- **T0** done: package `soup/`, `SOUP_DATA`, mmap, 25 pytest checks, matrix sha256 identical to the original code.
- **T1** done: streaming system `soup/stream/` (file queue, searchers, staged verifiers, supervisor writing
  `logs/stats.jsonl`, `journal/journal.md`, `journal/leaderboard.md`). Runs: `test10`, `fix5`, `e10` (REPORT.md).
  Known behaviour: searchers out-produce verifiers ~30x; the push gate and queue cap handle it; low-priority
  theories are never verified (a selection effect to state in T4).
- **T2** done: E 3.2.5, Vampire 5.1.0, Prover9/Mace4 LADR-2026-8A, all built from pinned source in the
  Containerfile. E is in stages b and c; Mace4 replaces z3 grounding for sizes 7–10 in stage c. Difficulty is
  still z3 effort (comparable with results-cloud); E proof steps recorded as `e_steps`.
- **A–D refuted**: E, Vampire and Prover9 all saturate; `soup/confluence.py` certifies convergent rewrite
  systems (infinite countermodels). Mace4 finds no finite countermodel up to 6–8 in 900 s, consistent.
- **Open-claim sweep**: 59 open claims → 25 proved, 2 refuted (certified), 32 survivors in 12 theories
  (`work/journal/survivors.md`).
- **Offline LLM step**: `prompts/survivors.md` is a self-contained prompt for an *external* LLM (the user
  may paste it into a cloud instance). Its output goes to `~/tmp/duet-offline/...`, never into the repo or
  `work/`. Policy in `prompts/README.md` and CLAUDE.md rule 6. **To do:** a checker
  (`soup/check_offline.py`) that reads that output and verifies each item: PROOF chains step by step with
  E/Vampire, FINITE_MODEL tables with `core.law_vector`, rewrite systems with `confluence`. Results go in a
  separate REPORT table marked "found offline with an LLM, machine-checked".
- **T4–T7** not started. T4 needs a preregistration commit before the run (arms prior / noprior exist:
  `--arm noprior`).

## Next steps, in order

1. Finish T3 (above); update REPORT.md and the paper's calibration paragraph (`tex/paper.tex`, `\pending{T3}`).
2. Write `soup/check_offline.py` when offline output exists.
3. Before T4: decide with the user whether to fix the score saturating on idempotence (all top theories have
   the emergent triple x·x = x, x∘x = x, x·x = x∘x). Any score change must be preregistered.
4. T4 preregistration, then the run (`run.sh stream --arm prior` and `--arm noprior`, seeds disjoint).
   Commit `work/journal/*.md` after every run (they are tracked; the rest of `work/` is not).

## Conventions that matter

- Everything inside Podman; host only `podman`, `git`, file edits. Small commits, push to origin main.
- The user wants dry, unslopped prose; numbers with the command that produced them; no claim of "new".
- Rebuild the image after code changes (`podman build -t soup .`): code is copied into the image, not mounted.
- Journal times are UTC (container clock); the Mac is CET.
