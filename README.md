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
- **The duality prior steers toward named structure (T4, preregistered).** With the prior, 330 of 998 verified
  theories are fragments of a named theory, nearly all of lattices. Without it, 31 of 393 are (one-sided Fisher
  p = 2e-25). The difference holds within each number of laws, which was checked post hoc.
- **An algebraist's profile (T5a, preregistered).** Of four structural features, only a convergent presentation
  separates named theories from random ones (6 of 10 against 13 of 120, Holm p = 0.002). It ranks the candidates.
- **What the top candidates turn out to be (post hoc).** New checks look for split theories (a ·-theory plus a
  ∘-theory, whose bridges only look like bridges), for hidden definitions, and for named theories under all 8
  relabellings.
  - 13 of 81 candidates are split, including the top-ranked one.
  - The second is an idempotent left quasigroup with ∘ written as the division.
  - Four more are absorption-type algebras without associativity.
  - One, `10c98c4b`, has a two-operation core: (x·y)∘(y·x) = x and (x∘y)·(y∘x) = x, meaning · is orthogonal to
    its transpose and ∘ decodes it (Schröder's second law when ∘ = ·), plus four absorption laws.
  - Web searches found no source for any of them, so they are candidates (`work/dossiers/`, with Lean
    certificates for their smallest models).
- **Not yet:** no theory found so far is new. The search's filters are syntactic: they let split theories and
  divisions in disguise through.

## Open problems

Each of these defeated E, Vampire, Twee (where run), Prover9 and finite-model search in our budgets. A proof, a
finite countermodel, or an infinite one with a checkable construction settles it. The budgets are in `REPORT.md`.

- **S12.** Do the four laws
  `x·(y∘(y∘(x∘y))) = x`, `x∘(y·(y·(x·y))) = x`, `(((x∘y)∘x)∘x)·y = y`, `(((x·y)·x)·x)∘y = y`
  imply `x·x = x∘x`? They do not imply `x·x = x`: a 10-element model refutes that (`tests/test_round2.py`). That
  model satisfies `x·x = x∘x`, so it does not answer this question. No model on 2–6 elements has `x·x ≠ x`
  (complete search), so the smallest one has 7–10 elements. With `x·y = x∘y` the laws become ETP Equations 437 and
  3115. Each alone has non-idempotent models, but no 2- or 3-element non-idempotent magma satisfies both. Whether
  the two together imply `x = x◇x` is still open after the follow-up runs (`REPORT.md`, Block 1).
- **The infinite-only non-implications** (A–D in the paper, and S1, S9, S11 in `REPORT.md`) are candidates
  for the TPTP library's non-theorem problems. Their countermodels are certified but necessarily infinite.

## License

Code: MIT (`LICENSE`). Text, paper and tables (`REPORT.md`, `PREREGISTRATION.md`, `tex/`): CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/).

## Status (22 Nov 2026, morning)

Nothing is running. All commits are local. Since the T4 tag, nothing has been pushed: `main` and `t4-prereg` were
pushed when T4 started, and later commits wait for the user.

Finished overnight (details and commands in `REPORT.md`, newest first):
- **T4** (preregistered, 4 h per arm at tag `t4-prereg`): H1 supported, 33% against 8% fragments.
- **T5a** (preregistered): only a convergent presentation separates named from random theories. It ranks the
  candidates.
- **X1** (exploratory, verifier V3): stopped by its memory rule after 1.5 of 4 h (deviation 4). 521 theories
  verified; Vampire FMB refuted 10 claims that stage a left open.
- **Candidates**: 81 profiled and ranked; equivalence checks `soup.hidden`, `soup.split`, `soup.relabel`;
  dossiers for the top 10 (`work/dossiers/`) with literature notes (`work/check/literature.json`); Lean certificates
  for their smallest models (`lean/`, 11 modules, audit passes).
- **Split scan of the T4 non-fragments** (post hoc): 35 of 668 in prior and 4 of 362 in noprior are split.

Disclosures from the night, all in `REPORT.md` or `PREREGISTRATION.md`:
- Deviation 3: OOM kills in the T5a profile run, handled by a rerun.
- Deviation 4: X1 was stopped early by its memory rule.
- A correction of the T4 crash list.
- Three slips of rule 1, all harmless. Twice an empty `python3 -` ran on the host; it did nothing. Once a read-only
  `python3 -c` on the host checked a JSON file.

Next, in order:
1. A filter for split theories and for divisions in disguise inside the search (the `soup.split` screen is cheap at
   2–4 elements), then a new preregistered run.
2. `10c98c4b`, the one candidate with a two-operation core: a literature search beyond the web, starting with
   Evans and Belousov on orthogonality identities; models of B alone; whether its absorptions have a natural
   meaning.
3. The assisted round-2 track: `tar -C ~/tmp/duet-offline/survivors-external01-2026-11-21 -cf -
   S10.md S12.md | podman run -i --rm -v "$PWD/work:/data:ro" soup python -m soup.round2 assisted >
   ~/tmp/duet-offline/survivors-external01-2026-11-21/round2_assisted.jsonl`. It uses the LLM's lemmas only after E
   proves each one.
4. T6 (S12 ⇒ x·x = x∘x), T7 (more Lean certificates, order-5 laws). A separate session is building a census of
   one-operation synergy pairs on ETP data (`work/census/`, its own branch, not merged here).

Task state: T0–T4 are done. T5 has its profile (T5a), ranking, equivalence checks and dossiers. T6 has one open
claim left. T7 has Lean certificates for 11 finite models.

Offline LLM work follows `prompts/README.md`: bundles live in `~/tmp/duet-offline/`, never in the repository or
`work/`, and count only after `soup.check_offline` (in their own REPORT table).
