# soup — genetic search over two-operation equational theories

Project memory for Claude Code. Read all of it before the first command, then `HANDOFF.md`.
Background note (literature, design, earlier results): https://claude.ai/artifact/3YweiTzEurAomActQxPUQB

## The question

Can an open-ended search over *theories* (small sets of equational laws over two binary
operations, written `x · y` and `x ∘ y`) find structure that humans would call interesting,
and in particular theories that are not already named? A law mixing both operations is a
*bridge*; bridges are where two theories fuse (absorption in lattices, distributivity, the
inverse operation of a rack). The measure of a successful fusion is *synergy*: laws implied
by the whole theory but by no single law of it.

## Hard rules

1. **Everything runs in Podman on the Mac.** Never `brew install`, `pip install`, or change
   anything on the host. Build tools, provers and Python packages go into the container image.
   The only host commands are `podman ...`, `git ...`, and reading/writing files in this folder.
2. Free software, actively maintained, lightweight. Pin versions.
3. Commit to git locally as you go (small commits, clear messages). No pushing unless asked.
4. Honest reporting: every claim in `REPORT.md` has a number, a script that produced it, and
   its caveats. Never call a theory "new" without a literature check and an equivalence check.
5. Preregister before any scaled run: hypotheses, arms, budgets, seeds, stop rules go in
   `PREREGISTRATION.md` and get committed *before* the run starts.
6. No LLM anywhere in the scoring loop. The search must stay contamination-free.
   Offline LLM work on results (e.g. `prompts/survivors.md`) writes outside the repo and outside `work/`;
   its output counts only after a machine check and never feeds back into the search (`prompts/README.md`).

## Environment

- Mac: 11 cores. Podman machine sized with `podman machine set --cpus 11 --memory 12288`.
- Image: `Containerfile` (python:3.13.18-slim; numpy 2.5.3, numba 0.68.1, z3-solver 5.4.1.0, pytest 9.0.1).
  z3 effort numbers depend on the z3 version: keep it pinned and never compare across versions.
  z3-solver 5.4.1.0 has an aarch64 wheel; the Mac reproduces absorption = 494, so effort numbers in
  `results-cloud/` are comparable (checked by `tests/test_named.py`).
- Code is copied into the image at `/app`; data lives in `work/`, mounted at `/data` (`SOUP_DATA`).
- Build and test: `podman build -t soup . && podman run --rm -v "$PWD/work:/data" soup bash run.sh test`
- Matrix (2.5 min on 11 cores): `podman run --rm -v "$PWD/work:/data" soup bash run.sh matrix`;
  `cd work && shasum -a 256 -c ../tests/matrix.sha256` must say OK for all three files.
- Streaming search: `podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 3600`
  (options `--searchers 3 --verifiers 8 --arm prior|noprior --seed0 101 --qmax 1500 --run <id>`;
  env `BUDGET`, `SEARCHERS`, `VERIFIERS`, `ARM`, `SEED0`, `RUN_ID`).
- Other scripts: `podman run --rm -v "$PWD/work:/data" soup python3 -m soup.calib` (env `CALIB_NULL`);
  same for `soup.fragments`, `soup.report`.

## Code (package `soup/`)

| File | Role |
| --- | --- |
| `paths.py` | `SOUP_DATA` (default `work/`); every file path goes through it |
| `laws.py` | Enumerates laws up to relabelling and side swap. Order ≤ 4, one op: 4694 (matches ETP). Two ops: 71,369, of which 61,983 bridges |
| `probes.py` | Deterministic corpus of 12,509 two-op structures on 2–6 elements (all on 2; affine pairs over ℤ/3–ℤ/6; 𝔽₄; Klein, S₃, ℤ/6 group-derived ops; lattices M₃, N₅, 2²; ℤ/n with +,×; random tables) |
| `matrix.py` | numba: law × structure matrix → `M_probe_major.npy`, `M_law_major.npy` (packed bits, ~111 MB each), `meta.pkl`, `nondeg.npy`; `evaluate_one` for single structures |
| `data.py` | Loads meta and the matrices (`mmap_mode='r'`, shared between processes), non-degeneracy mask, TPTP export |
| `core.py` | `Corpus` (base + found structures as packed law vectors; optional shared store `corpus/<n>_<hash>.npz` with `refresh()`), `law_vector`, `prove` (fresh z3 context, returns effort), `Grounding`/`find_model` (grounded finite models in their own context) |
| `verify.py` | Stages a (census, independence and claim countermodels to size 6), b (bounded z3 proofs, score), c (sizes 7–8, long z3); `verify` = a+b; `LEGACY` = first-session settings |
| `named.py`, `duality.py` | Law parser, named theories; dualities, `canonical(T)` and `theory_key(T)` up to the three dualities |
| `calib.py`, `fragments.py`, `report.py` | Calibration, fragment check, summary (ported, outputs in `SOUP_DATA`) |
| `loop_dual.py` | First-session batch MAP-Elites (superseded by `stream/`) |
| `stream/fqueue.py` | File priority queue: `queue/{pending,stage2c,claimed,seen,dropped}` |
| `stream/searcher.py` | Continuous MAP-Elites, pushes every cell win with a bridge; verified scores replace cheap ones |
| `stream/verifier.py` | Pulls tasks, runs stages a+b or c, writes `results/<key>.json`, models to the corpus |
| `stream/supervisor.py` | Starts and rebalances processes; single writer of `logs/stats.jsonl`, `journal/journal.md`, `journal/leaderboard.md` |

Data in `work/` (not in git): matrix files, `corpus/`, `queue/`, `results/`, `journal/`, `logs/<run>/<worker>.log`,
`logs/stats.jsonl`, `logs/workers/*.json` (heartbeats), `runs/<run>/` (config, archive snapshots).
`results-cloud/` (in git): results from the first sessions (cloud, 2 cores, z3 5.4.1).

## What is already known (21 November 2026)

- **Calibration lattice check:** lattice absorption pair ⇒ both operations idempotent (synergy), z3 effort 494.
  Model census gives 1, 1, 2 lattices on 2, 3, 4 elements (correct).
- **Calibration (partial, 35 random theories):** all 6 named theories (lattice, skew lattice, dimonoid,
  absorption pair, left and right quasigroup) have a duality; 0 of 35 random ones do. On synergy,
  difficulty and model counts the named theories sit at the 9th–91st percentile: difficulty does not
  separate named from random, symmetry does. The 6-law null sample was not finished.
- **Duality-prior search (9 rounds, 2 cores):** 99 verified theories; 64 of the 97 with a proved emergent
  law are lattice fragments, 8 skew-lattice fragments, 0 dimonoid fragments. Earlier run without the prior
  (also without the definitional filter, ≤ 4 laws): 6 of 59. 921 structures added to the corpus.
  21 emergent claims in 16 theories open (no proof, no countermodel ≤ 4).
- **Top non-fragment finds:**
  - T1 = {(x·x)∘x = x, ((x·(y·z))∘z)·y = y} forces x·x = x, x∘x = x, x·x = x∘x; effort 134,513.
  - T2 = {x∘(y·(y∘x)) = x, x·((x∘x)·y) = x} forces the same; effort 11,827.
  - Both have no duality and no non-degenerate model on 2 elements, but ≥ 8 on 3 and on 4.
- **Open implications from the pilot** (goal x·x = x; no z3 proof in 120 s):
  - A: x·(x∘x)=x; x∘(x∘y)=y; ((x∘y)∘x)·y=x. No countermodel ≤ 6; no affine one over ℤ/n, n ≤ 16.
  - B: (x·y)·y=x; (x·x)∘x=x; x∘(y·(x·y))=y.
  - C: x·(x·x)=x; (x·y)·y=x; (x∘y)·(y∘x)=y. No countermodel ≤ 7; no affine one, n ≤ 24.
  - D: x·(x∘x)=x; (x∘y)·x=y; x·((y∘y)∘x)=x.
- **Classical follow-up (21 Nov, morning):**
  - The search rediscovered L1 x·(y∘(x∘z)) = x and L2 x∘(y·(x·z)) = x of McKenzie's 1970 4-basis for
    lattices (· = join, ∘ = meet; L3 ((y∘x)·(x∘z))·x = x, L4 ((y·x)∘(x·z))∘x = x; see
    https://www.cs.unm.edu/~veroff/LT). The search's variants of the basis do NOT force commutativity:
    countermodels on 5 elements. z3 proves commutativity from McKenzie's basis with effort 8.5M (328 s).
  - Prior art for the whole method: McCune and Padmanabhan, *Automated Deduction in Equational Logic and
    Cubic Curves* (LNCS 1095, 1996), and McCune, Padmanabhan, Veroff, "Yet another single law for
    lattices" (enumerate identities, filter through non-lattices, prove). Read both before T4.
  - T1 and T2 have 3- and 5-step human proofs (one law manufactures local identities or zeros, the
    other uses them). z3 effort measures instantiation search, not depth: T1's hardest step is one
    substitution and costs 144,631. Difficulty must come from saturation-prover proof length (T2).
  - Re-check of the 21 open claims with countermodels on 5–6 elements: 8 false, 6 undecided, 7 open.
  - A: no countermodel ≤ 8. Under x∘(x∘y) = y, A's third law is equivalent to C's (x∘y)·(y∘x) = y.
- **Facts confirmed:**
  - Lattice associativity is independent of the other five lattice axioms; the smallest countermodel found has 5 elements.
  - The two one-sided quasigroup laws are independent, but only infinite models show it.

## Pitfalls already paid for

- z3's `rlimit count` is cumulative per context: one fresh `z3.Context()` per proof.
- z3 with quantifiers over a finite sort hangs or runs out of memory: ground the axioms instead.
- Countermodel search to size 4 is too short: 8 "open" claims fell at size 5–6. Search to at least 6
  (grounded z3 handles 5–8 quickly for laws with ≤ 3 variables; use Mace4 beyond).
- A thin corpus produces false "emergent" laws (14 claims in 6 theories were refuted at size 3–4):
  countermodel-check every claim before scoring it; add every model found to the corpus.
- Collapse: theories forcing an operation to ignore an argument make thousands of laws emergent.
  Require a model with two distinct, essentially binary operations.
- Definitional theories (one operation a term in the other, e.g. x∘y = y·x) are not fusions: filtered.
- Ubuntu's `eprover` 3.0.03 package is a debug build that crashes at start. Test any prover first.
- Finite-model search cannot refute claims whose countermodels are infinite (A–D: none up to size 8).
  Run E first: a saturation (CounterSatisfiable) plus `soup.confluence` settles it in seconds.
- E exit code 8 is "resource out", not a crash. GitHub archive tarballs lack submodules (Vampire needs
  viras and cadical): clone at a pinned commit instead.
- Uniform rejection sampling of random theories is infeasible at 6 laws (0 accepted in 267,682 draws).
- `ProcessPoolExecutor.map` returns in order: one slow job blocks all output. Use `as_completed`.
- z3 calls are not interrupted by Python signal handlers; the stop watcher (wakeup fd + `ctx.interrupt()`)
  is what makes SIGTERM work. z3 grounding at size ≥ 6 with 5–6 variables can take > 2 GB: capped.
- One OOM-killed worker breaks a whole `ProcessPoolExecutor` (T3 died at 69/130). Long batch runs: one child
  process per item, every prover under `SOUP_PROVER_MEMORY_MB`, z3 under `set_memory_limit`. The VM kernel
  log (`podman machine ssh journalctl -k`) shows OOM kills; start long containers without `--rm` to keep logs.
- Prover9's empty sos is not a saturation if `max_weight` deleted clauses (default 100; S12 lost 8,216 of
  8,561). Count `Deleted_by_rule`. Prover9 `max_megs` (200) and Mace4 `-b` (500) defaults silently cap runs.
- "No countermodel up to size n" must list the sizes where the search ran out of budget (`cm_unknown_sizes`);
  9 of 12 survivor theories had size 6 unsearched, and S4 had a 5-element countermodel.
- A claim only E proved got z3's budget cap as difficulty: the top of the V1 leaderboard is that artifact.
- Vampire 5.1.0 has no `--mode casc_sat`; use `--mode portfolio --schedule casc_sat`.
- Offline LLM bundles live in `~/tmp/duet-offline/<name>/`, are read by `soup.check_offline` from a tar on
  stdin (no container mounts them), and are ignored by git and the build context.

## Tasks, in order

- **T0 – Repo hygiene.** `git init`. Make paths relative (package `soup/`, data dir from an env var).
  Load matrices with `np.load(..., mmap_mode='r')` so processes share pages (today each process
  needs ~750 MB). Add a few pytest checks: 4694 one-op laws, lattice model counts 1/1/2, absorption
  synergy proved, duality of the six named theories. Run tests in the container.
  Done when `podman run ... pytest` passes and the matrix rebuild reproduces `meta.pkl` byte-for-byte
  in law order (check a hash).
- **T1 – Shared growing corpus and streaming verification.** An append-only directory of found
  structures (`corpus/<n>_<hash>.npz`), reloaded by every process often. Replace the batch rounds
  (90 s search, then verify 12) with a stream: every theory that wins or improves an archive cell is
  pushed at once to a verification queue (deduplicated up to the three dualities; priority by score and
  novelty). Verifier processes pull from it in three stages: 2a countermodels to size 6 and independence
  (seconds); 2b bounded prover run, proof length as difficulty; 2c only for survivors left open —
  Mace4 to size 8–10, long prover runs. Every countermodel goes to the corpus immediately, and the
  verified score replaces the cheap score in the archive. Start with 3 search and 8 verifier
  processes on 11 cores, then rebalance by queue length. A plain file-based queue is enough on one
  machine; Valkey if it ever goes distributed.
- **T2 – Better provers, inside the container.** Try, in this order: E (Debian package or source
  build), Vampire (source build, BSD), Prover9/Mace4 (LADR). Keep whichever passes the absorption
  test and the four open implications A–D smoke test. Use prover output for a second difficulty
  measure (proof length in inferences), deterministic, and cross-check against z3.
- **T3 – Finish the calibration.** 30 random theories per size (2, 5, 6), plus more named theories
  that fit order ≤ 4 (e.g. bisemilattices with absorption variants, one-sided quasigroups with
  idempotence). Report Fisher's exact test for "has a duality" and percentiles for the rest.
- **T4 – Preregister, then scale the duality-prior search.** 10 processes, several hours, matched
  control arm without the prior (same filters, same law cap). Primary outcome: share of verified
  theories that are fragments of a named theory, per arm. Secondary: top non-fragment theories by
  score. Merge archives across seeds; deduplicate theories up to the three dualities and up to
  logical equivalence (prover both ways).
- **T5 – Look hard at T1, T2 and the new top finds.** Model counts on 2–7 elements, automorphisms,
  whether a known variety is equivalent (implies and is implied by its laws), and a literature
  search. Write what is found, including "already known as X".
- **T6 – Open claims.** A–D and the 21 open claims: longer prover runs, Mace4 to size 8–10,
  affine and group-derived countermodel families. Each one ends as proved, refuted, or open with
  the budget stated.
- **T7 – Later.** Order-5 laws (count them first and estimate the matrix in RAM before building),
  or a unary operation. Lean 4 certificates for finite countermodels (`decide`) and for the best
  implications.

## Reporting

`REPORT.md` holds the current numbers, one table per task, newest first, each with the command
that produced it. Keep `work/report.txt` as the raw output of `report.py`.

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |
