# duet: searching for synergy between two binary operations

> **Work in progress.** A research log, not a finished result. No theory found so far is claimed to be new, the
> paper in `tex/` is a draft, and `REPORT.md` gives every number with its caveats and the command behind it.

An open-ended search over small equational theories in two binary operations, `x · y` and `x ∘ y`. Laws go up to
order 4: 71,369 laws up to renaming, 61,983 of them *bridges* that mix both operations. The search looks for theories
whose laws together imply laws that no single law implies (*synergy*). The reference case is the lattice absorption
pair, which forces both operations to be idempotent. Every claim goes through finite-model search and theorem
provers before it is reported. No language model is used in the search or its scoring.

**New to the subject?** [`intro/intro-reading.pdf`](intro/intro-reading.pdf) builds the background from sets and
functions, in 9 pages, up to how the search works and why it could matter. The same text with exercises and
solutions is [`intro/intro.pdf`](intro/intro.pdf).

## Running it

Everything runs inside Podman; nothing is installed on the host. Code is in the `soup/` package. Data lives in
`work/`, mounted at `/data`.

    podman build -t soup .
    podman run --rm -v "$PWD/work:/data" soup bash run.sh test            # builds the matrix first if missing
    podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 3600

The image carries z3 5.4.1 and five provers built from pinned sources: E 3.2.5, Vampire 5.1.0, Prover9/Mace4
LADR-2026-8A and Twee 2.7.1. A stream run writes:
- `work/journal/` (journal and leaderboard);
- `work/results/` (one verified theory per file);
- `work/corpus/` (every structure found).

Where to look:
- **`REPORT.md`:** results, newest first.
- **`PREREGISTRATION.md`:** hypotheses fixed before each run, and the deviations.
- **`CLAUDE.md`:** rules, code map and task list.
- **`notes/`:** analysis scripts and memos.
- **`lean/`:** Lean 4 certificates.
- **`tex/`:** the draft paper.

## Results so far (details in `REPORT.md`)

- **Rediscovery.** The search finds lattice theory in pieces: two of the four laws of McKenzie's 1970 basis, 12
  different lattice bases, 26 axiomatizations of the absorption pair (counted per run), and Fried's weakly associative
  lattices.
  Against a catalogue of 13 known structures fixed in advance, it rediscovered 7.
- **Calibration (preregistered).** Named theories have a syntactic duality and random ones don't (8 of 10 against
  0 of 120). A duality prior raises the share of verified theories that are fragments of a named theory from 8% to
  33% (p = 2 × 10⁻²⁵).
- **Non-implications that finite search cannot settle.** Four pilot implications are false, and their
  countermodels are necessarily infinite. Saturating provers settle them, and an independent check certifies the
  saturations.
- **Survivor claims.** Of 32 claims that resisted the provers, 31 are refuted:
  - by finite models (up to 13 elements), by models on ℤ, or by one hand proof that is sampled but not certified;
  - some of the refutations came from an LLM outside the pipeline, machine-checked before they count;
  - one claim is still open (below).
- **Top candidates.** Most top candidates turn out to be disguises: split theories, divisions written as a second
  operation, or absorption-type subvarieties. Two cores are prior art:
  - `10c98c4b`'s core is the Δ-bijectivity of the Yang–Baxter literature.
  - `31d6d970` plus associativity is the rectangular skew lattices; the full theory has no source found.
- **A diagonal attractor.** Up to X3, 97% of the scored theories proved an emergent law in one variable, such as
  `x·x = x∘x`, and none proved emergent associativity. The score was rewarding what a fusion forces on x·x.
- **Leaving the named corner (X4).** A new search arm counts only synergy that does not go through the diagonal, and
  skips the lattice corner. It also builds a quarter of its proposals from a law of `·`, a law of `∘` and a bridge.
  - **Results:** 636 theories verified, and none of the 565 scored ones is a fragment of a named theory (X3: 31.6%).
    Only 3 were split.
  - **Less charted ground:** finite models refute 21% of its claims, against 3% in X3.
  - **The attractor moved:** the most common laws now say a left translation sends a family to x·x, as in
    `x·(x·y) = x·x`.
- **Scale.** All runs together verified 4,222 theories, against 1.8 × 10²⁶ law sets of up to six laws. The search
  has mostly seen the corner humans know best, and "no source found" is weak evidence.

## Candidates (live)

<!-- candidates:start -->
*Not computed yet. The novelty ranking N1 (PREREGISTRATION.md, N1) runs after X4's checks, and this block is
regenerated each time it runs.*
<!-- candidates:end -->

## Open problems

Each defeated E, Vampire, Prover9 and finite-model search in our budgets. A proof, a finite countermodel, or an
infinite one with a checkable construction settles it.

- **S12.** Do `x·(y∘(y∘(x∘y))) = x`, `x∘(y·(y·(x·y))) = x`, `(((x∘y)∘x)∘x)·y = y` and `(((x·y)·x)·x)∘y = y` imply
  `x·x = x∘x`?
  - They do not imply `x·x = x`: a 10-element model refutes it (`tests/test_round2.py`). That model satisfies
    `x·x = x∘x`.
  - No model on 2–6 elements has `x·x ≠ x`.
  - With `x·y = x∘y` the laws become ETP Equations 437 and 3115, and whether they imply `x = x◇x` is also open.
- **Infinite-only non-implications** (A–D, S1, S9, S11 in `REPORT.md`): candidates for the TPTP library's non-theorem
  problems, with certified but necessarily infinite countermodels.

## Status (22 Nov 2026, late afternoon)

- **Done today:**
  - X3 (verifier V4, the disguise filters);
  - X4 (the fusion arm), which ran to budget after a 3-minute false start exposed the loophole `x·x = y·y`
    (deviation 6);
  - the rediscovery measure R1 (7 of 13 catalogued structures);
  - the introduction [`intro/intro-reading.pdf`](intro/intro-reading.pdf);
  - the paper draft, updated through X4.
- **Running:** X4's preregistered checks on its 20 candidates (profile, hidden definitions, split, relabelling).
- **Next:**
  - the rediscovery check and split scan on X4;
  - merging candidates that are the same variety (`soup.dedupe`);
  - the novelty ranking N1, which fills the live section above.
  - Later: the open claims (T6) and more Lean certificates (T7).

`main` is pushed to the private origin at each milestone. Offline LLM work follows `prompts/README.md` and counts only
after a machine check. Deviations and slips are disclosed in `PREREGISTRATION.md` and `REPORT.md`.

## License

Code: MIT (`LICENSE`). Text, paper and tables (`REPORT.md`, `PREREGISTRATION.md`, `tex/`, `intro/`): CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/).
