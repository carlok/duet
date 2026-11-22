# duet: can a machine find new ways for two operations to work together?

> **Work in progress.** This is a research log, not a finished result. No theory found so far is claimed to be new.
> The paper in `tex/` is a draft. `REPORT.md` gives every number with its caveats and the command behind it.

Many familiar structures in algebra are two operations held together by a few laws. Take a lattice, such as `max` and
`min` on numbers, written `x · y` and `x ∘ y`. Two *absorption laws* tie them together: `x · (x ∘ y) = x` and
`x ∘ (x · y) = x`. Neither law alone says anything about `x · x`, yet together they force `x · x = x`. The whole
implies something no part does: that is **synergy**. Laws that mix both operations are **bridges**, and bridges are
where two theories fuse into one structure.

**duet asks whether an open-ended search can find such fusions, and in particular ones nobody has named yet.** No
language model takes part in the search. It explores small theories in two binary operations and checks every claim
with theorem provers and finite models. It also keeps an honest ledger of what it finds, including everything that
turns out to be already known.

**New to the subject?** [`intro/intro-reading.pdf`](intro/intro-reading.pdf) explains it all from sets and functions, in 9
pages: laws, theories and models, synergy, and how the search works. The same text with exercises and solutions is
[`intro/intro.pdf`](intro/intro.pdf).

## How the search works

- **The space.** It covers every law of order at most 4 (at most four operation symbols): 71,369 up to renaming,
  61,983 of them bridges. A theory is a set of 2 to 6 such laws.
- **A cheap guess at implication.** We record once which laws hold in each of 12,509 small structures on 2–6 elements.
  To guess what a theory implies, look at the structures that satisfy it and collect the laws true in all of them.
  This is only a guess, and every countermodel found later is added to the collection.
- **The search.** It uses MAP-Elites, a quality-diversity algorithm. Theories are sorted into cells by a few
  features, each cell keeps its best theory, and new theories come from mutating and combining old ones.
- **Verification.** Every promising theory goes to verifier processes:
  1. small models, independence of the laws, and countermodels on up to 6 elements to each guessed emergent law;
  2. the prover E;
  3. Vampire's finite model builder;
  4. Mace4, up to 10 elements.

  A prover saturation, checked independently, settles claims that only infinite models refute. Only proved laws count.
  Lean 4 certifies the smallest models of the top candidates and proves the general statements.
- **Discipline.** Every scaled run is preregistered before it starts (`PREREGISTRATION.md`), and deviations are listed
  there. Every number in `REPORT.md` has the command that produced it.

## What happened

**1. It rediscovers lattice theory.** The first runs found lattice theory in pieces:
- two of the four laws of McKenzie's 1970 lattice basis, and 12 different lattice bases;
- 26 axiomatizations of the absorption pair (counted per run);
- Fried's weakly associative lattices.

Against a catalogue of 13 known two-operation structures fixed in advance, it found 7. Named theories have a
syntactic duality and random ones don't (8 of 10 against 0 of 120). A prior that rewards dualities raises the share of
verified theories that are fragments of a named theory from 8% to 33% (preregistered, p = 2 × 10⁻²⁵). Rediscovery is
the calibration: the search finds what humans found.

**2. Its best candidates were disguises.** The top candidates that were not fragments turned out to be old
structures in disguise:
- split theories: a theory of `·` beside a theory of `∘`, whose bridges only look like bridges;
- one-operation structures with their division written as `∘`;
- absorption-type subvarieties.

One core came from a distant field: `10c98c4b`'s is the Δ-bijectivity of the Yang–Baxter literature. Filters for the
first two disguises went into the verifier (run X3). Afterwards none of X3's 570 scored non-fragments is split, against
33 of 654 before. The automatic checks recognise fewer of its top candidates: 26%, against 50%.

**3. It had learned one trick.** 97% of all scored theories proved an emergent law in one variable, such as
`x · x = x ∘ x`, and none proved emergent associativity. The score was rewarding what a fusion forces on squares, and
the lattice reference case itself is of that kind. So a new arm, *fusion* (run X4), was built:
- **Score:** it counts only synergy that does not come from the diagonal.
- **Lattice corner:** theories valid in the 2-element lattice are skipped.
- **Proposals:** a quarter of them are a law of `·`, a law of `∘` and a bridge, two traditions and a link between
  them.

Its first 3-minute attempt found the next loophole (`x · x = y · y`). It was restarted with a wider definition, which
is deviation 6. Results:
- none of its 565 scored theories is a fragment of a named theory (X3: 31.6%);
- finite models refute 21% of its claims, against 3%: less charted ground;
- the attractor moved instead of disappearing (`x · (x · y) = x · x` and its kin).

**4. Ranking for novelty, then looking closely.** A second, preregistered ranking, N1, ranks the candidates that work
and that no check identifies (live, below). Several were then dug into one by one:
1. a plain reading proved with E;
2. models from known constructions;
3. a targeted literature search;
4. Lean proofs of the general statements.

Each one examined so far turned out to be related to known mathematics, which the search reached without knowing it:
- **`10c98c4b`:** its core is a Δ-bijective pair, from the Yang–Baxter literature (Rump; Bonatto et al.).
- **`31d6d970`:** the same variety as `2dc27508` and `69dfbd8e`, found three times. With associativity it is exactly
  Leech's rectangular skew lattices.
- **`a9295908`:** a fragment of Heyting algebras. With `·` = ∧ and `x ∘ y = (y → x) → y`, every Heyting algebra is a
  model (Lean). On chains, that `∘` is the strict-order connective of Gödel logic.
- **`55cb2c91`:** not identified, related in pieces only (ETP Equations 327 and 378).
  - Its one-operation shadow is trivial: with `· = ∘` it has only one-element models.
  - Its `∘` is a partial swap `y · x ↦ x · y`.

**Along the way:**
- **Infinite countermodels.** Four early implications turned out false with only infinite countermodels, settled by
  saturating provers and an independent certificate.
- **Survivor claims.** Of 32 claims that resisted the provers, 31 are now refuted, and one is open (S12, below). Some
  refutations came from an LLM working offline, outside the search, and count only after our own machine check.

**Where this leaves the question.** No theory is claimed new. The searches have verified about 5,000 theories,
against about 1.8 × 10²⁶ possible law sets, mostly in the corner humans know best. "No source found" by our web
searches is weak evidence. A specialist's eye is the missing check.

## Candidates (live)

<!-- candidates:start -->
*Regenerated by `soup.novelty` after each run's checks; last update 22 Nov 2026, 21:07 UTC. Full tables: [`notes/candidates_table.md`](notes/candidates_table.md).*

The candidate pool holds the top 20 non-fragments of each run: 138 theories. **56 are known**: 35 related to a named or catalogued structure, 14 split, 6 same variety as another candidate, 1 identified by hand (ledger). **77 are not known as far as our checks go**, and are ranked below. 3 fail "works" and 2 have no verification record.

**Metric (N1, preregistered).** A candidate enters only if it works, meaning it has a proved emergent law and non-degenerate models on two or more sizes, and no check identifies it. It is then ordered by:
1. a proved emergent law off the diagonal, meaning not just a statement about x·x and x∘x;
2. no model among the classical constructions: affine, group-derived, lattices, rings;
3. no partial identification by hand;
4. more sizes with non-degenerate models;
5. smaller axioms;
6. verified score.

"Not known" is not "new". It means our checks and catalogue found nothing. Web searches have been run only for some top entries, and they are weak evidence.

| N1 | theory | run | off-diagonal law | classical model | partly known as | sizes | T5a rank | literature |
|---|---|---|---|---|---|---|---|---|
| 1 | `55cb2c91`: x · (x ∘ y) = x & x · y = ((y · z) · x) ∘ x | . | (x · y) · y = x · y | no | - | 3 | 98 | Related in pieces only |
| 2 | `1d0a5211`: x · (x ∘ y) = y ∘ x & (x ∘ (y · z)) ∘ z = z | . | x · (x ∘ (y · x)) = x | no | - | 3 | 107 | Nothing found |
| 3 | `a9295908`: x · (x ∘ x) = x & (x ∘ y) · y = y & x · y = x ∘ (y · x) | t4-prior | x · (x · y) = x · (y · x) | no | - | 3 | 86 | Related: a fragment of Heyting algebras |
| 4 | `742cc445`: x · (y ∘ (x ∘ z)) = x & x ∘ ((x ∘ y) · (z ∘ x)) = x | x4 | x · (x · x) = x ∘ (x ∘ y) | no | - | 3 | 117 | Related only |
| 5 | `97a7dfcf`: x · x = y · y & x · (y ∘ x) = x ∘ y & (x · y) · z = y ∘ (z · y) | x4 | x · (x · x) = x ∘ (x · y) | no | - | 3 | 116 | Nothing found |
| 6 | `7ec7f8f5`: x · (y ∘ x) = x ∘ y & x · (y · x) = (x · x) ∘ z & (x · y) · z = (z ∘ x) ∘ x | x4 | x · (y · x) = x ∘ (x · y) | no | - | 3 | 110 | Nothing found |
| 7 | `f79a5097`: x · (y ∘ x) = x & x ∘ ((x ∘ y) · y) = x & x ∘ ((x · y) ∘ x) = x & x · ((y ∘ y) ∘ (y · x)) = x | x4 | x · (x · x) = x · (x ∘ y) | no | - | 3 | 34 | Related only |
| 8 | `7c476118`: x · ((y ∘ x) ∘ z) = x & (x · y) ∘ (x ∘ y) = x | x4 | x · (x · x) = x · (x · y) | no | - | 2 | 129 | Nothing found |
| 9 | `a8963027`: x · (x · y) = x & x ∘ (y ∘ x) = x & x ∘ (y · (x · (x ∘ z))) = x | x4 | x · (x · x) = x ∘ (x · y) | no | - | 2 | 35 | Nothing found |
| 10 | `3b3b1176`: x · (x · y) = x ∘ x & x · x = y ∘ (x ∘ y) & x · y = (y · x) ∘ y | x4 | x · (x · x) = x ∘ (y · x) | no | - | 2 | 121 | Nothing found |
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

## How this was made

An AI coding assistant (Claude Code, by Anthropic) designed, coded, ran and wrote most of this project, directed and
reviewed by the author. The commits carry `Co-Authored-By` trailers, and [`CLAUDE.md`](CLAUDE.md) is the assistant's
working memory: rules, code map, facts and the pitfalls it ran into.

**No language model takes part in the search or its scoring** (rule 6 in `CLAUDE.md`). Language models were used outside
it in two ways:
- **Offline LLM work.** An external model worked on the 32 survivor claims, following
  [`prompts/README.md`](prompts/README.md). Its answers count only after `soup.check_offline` verifies them.
- **Literature lookups.** Web-only AI agents searched the literature, and their key claims were rechecked by machine.

Every claim here rests on prover proofs, finite models or Lean, never on a model's word.

## Where it stands (22 Nov 2026, night)

- **Latest:**
  - the fusion arm X4;
  - the novelty ranking N1, with literature checks of its top 10;
  - close looks at `a9295908` (identified) and `55cb2c91` (related in pieces);
  - the introduction;
  - the paper draft, through N1.
- **Next:**
  - a search that steers away from X4's new attractor;
  - close looks at N1's other entries;
  - the open claim S12 (T6) and more Lean certificates (T7).
- Deviations and slips are disclosed in `PREREGISTRATION.md` and `REPORT.md`.

## Running it

Everything runs inside Podman; nothing is installed on the host. The code is the `soup/` package. Data lives in `work/`,
mounted at `/data`.

    podman build -t soup .
    podman run --rm -v "$PWD/work:/data" soup bash run.sh test            # builds the matrix first if missing
    podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 3600

The image carries z3 5.4.1 and five provers built from pinned sources: E 3.2.5, Vampire 5.1.0, Prover9/Mace4
LADR-2026-8A and Twee 2.7.1. A stream run writes `work/journal/` (journal and leaderboard), `work/results/` (one
verified theory per file) and `work/corpus/` (every structure found).

## Where to look

- **`REPORT.md`:** results, newest first, each with its command and caveats.
- **`PREREGISTRATION.md`:** the plans fixed before each run, and the deviations.
- **`notes/`:** analysis scripts and memos. Start with `notes/rediscovery.md`, the ledger of everything that turned
  out to be known, and `notes/candidates_table.md`.
- **`lean/`:** Lean 4 certificates and general proofs.
- **`tex/`:** the draft paper. **`intro/`:** the introduction.
- **`CLAUDE.md`:** the assistant's rules, code map and task list.

## License

Code: MIT (`LICENSE`). Text, paper and tables (`REPORT.md`, `PREREGISTRATION.md`, `tex/`, `intro/`): CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/).
