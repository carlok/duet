# Preregistration

Each section is committed before its run starts. Changes after the start are listed under "Deviations".

## Review items B1, B3, C3, C4 (written 28 Nov 2026, 08:15 UTC, approved by the user, before anything is computed)

Post hoc, from the external review of 279157e (REPORT, "N2"). Drafts: `notes/prereg_draft_BC.md`, which keeps the items
not approved (B2, B4, B5, B6, C1, C2). Two corrections to the approved drafts were made before this commit:
- C3's structure list is replaced. Four of its eight structures were wrong for the purpose:
  - Brouwerian semilattices would be caught by R2's Heyting algebras, and Kleene lattices by R1's lattices;
  - near-rings and bisemilattices have no bridge of order ≤ 4.
- B3's rectangularity is the exact ratio, not a sample, and k(F) is counted by an explicit search.

A mark from B3 that separates in calibration becomes a candidate key of a later ranking, N3, preregistered on its own.
N1, N2, F1 and the funnel are not changed. Nothing runs beside a stream run, and at most 4 prover jobs run at once,
with `podman stats` checked first.

### R2: a library of structures beyond the law table, and `soup.interp` (review B1)

**Question.** How many candidates are fragments of a classical structure under a term interpretation that the order-4
law table cannot express?

**Entries, fixed here.** Each entry is a TPTP axiom set in its own signature, with constants and unary operations
allowed.
- G: groups. AG: abelian groups.
- R: rings with 1. CR: commutative rings. BR: Boolean rings.
- DL: distributive lattices. BA: Boolean algebras. HA: Heyting algebras. Hp: hoops (·, →, 1).
- Rk: racks. Qd: quandles (▷ and its inverse).
- Qg: quasigroups (·, \, /).

Axioms come from the TPTP library (ALG, GRP, LAT, RNG) where it has them, otherwise from Jipsen's Mathematical
Structures pages. Each source is cited in `soup/interp.py`.

**Term pairs.**
- **Terms:** the binary terms in x, y of each entry's signature with at most 3 operation symbols (constants and unary
  operations count), that depend on both x and y, up to equality in the entry (E, 10 s).
- **Pairs:** (·, ∘) ranges over ordered pairs of distinct such terms.
- **BA:** the 10 essentially binary Boolean functions, which give 90 ordered pairs.

**Test.** "T is a fragment of (K; t1, t2)", in two stages.
1. **Model filter:** Mace4 models of K on sizes 2–6, up to 200 per size, 120 s per size. t1 and t2 are evaluated to
   tables, and every law of T must hold in every model (`law_vector`).
2. **Proof:** E proves each law of T, translated through t1 and t2, from K's axioms. 60 s per law, then Vampire 60 s for
   what E leaves.

The result is "fragment" (all laws proved), "not" (a model of K fails a law) or "unknown".

**Hypotheses.**
- **R2a, positive control:** with no hint, `a9295908` comes out as a fragment of HA with · = ∧ and
  x∘y = (y→x)→y.
- **R2b, calibration:** none of T3's 120 random theories is a fragment of an R2 entry.
- **R2c, descriptive:** the number of N2's level-6 and level-7 theories that are fragments, by entry.

**Budget:** 8 h of wall time. Entries are run in the order listed.

### Free (review B3)

**Measures,** for ∘ given · and for · given ∘:
- **Counting:** for a reduct F, the tables G with (F, G) ⊨ T are enumerated by a backtracking search over G's cells.
  Every law instance is checked as soon as its cells are assigned. The count k(F) is capped at 100,000.
- **Choice entropy:** H = mean over F of log k(F) / (n² log n).
- **Rectangularity:** ρ = mean over F of k(F) / ∏ |S_xy|, where S_xy is the set of values cell xy takes in F's models.
  ρ = 1 means the model set is a product over cells. For a capped F, ρ is estimated from 200 seeded draws from the
  product (`split.holds`), and flagged.
- **Reducts:**
  - n = 3: every magma F with k(F) > 0 (exhaustive);
  - n = 4: 200 distinct ·-tables, drawn with seed 0 from Mace4's models of T (up to 20,000).
- **Certificate:** T proves s·(x∘y) = s·t(x,y), or (x∘y)·s = t(x,y)·s, for some ·-term t with at most 2 symbols.
  Model filter, then E 30 s per t.
- **Wall time:** 600 s per theory and direction. A theory past its limit is reported as incomplete.

**Calibration set:** the catalogue's order-4 entries (`soup.catalogue`, 13 entries) and T3's 120 random theories.

**Hypotheses.**
- **F1:** the catalogue entries have a lower H, and a lower ρ, than T3's random theories. Mann–Whitney, two-sided,
  p < 0.01, for each measure.
- **F2:** on N2's level 7, H and ρ are higher than on T3's random theories.
- **F3:** among N2's level-7 theories, those with non-degenerate models on 4 sizes have a higher H than the rest
  (Mann–Whitney, descriptive).

A measure that passes F1 becomes a candidate N3 key.

### A false-novelty rate (review C3)

**Test structures,** fixed here. Each is known, outside R1 and R2, and has bridge laws of order ≤ 4. Axioms come from
the TPTP library or Jipsen's pages:
- Moufang loops (·, \);
- left Bol loops (·, \);
- commutative Moufang loops (·, \);
- groups with (xy, x⁻¹y⁻¹xy), whose commutator term is beyond R2's 3 symbols;
- cycle sets with the inverse translation (·, ∗; Rump 2005);
- Lie rings (+, [ , ]);
- idempotent semirings (+, ·).

**Fragments.** For each structure K:
- the true laws are the laws of the table that hold in K's Mace4 models (sizes 2–6, 200 per size) and that E proves
  from K's axioms (60 s);
- the fragments are seeded random sets of 2–4 true laws, at least one of them a bridge, under a random relabelling;
- a fragment is kept when it passes the search's own cheap test: an off-diagonal emergent law on the union corpus.
  Draws stop at 10 kept fragments, or at 5,000 draws;
- duplicates under `theory_key` are dropped.

**Procedure.** In a fresh directory, `work/fn-test`:
1. the kept fragments are pushed to the queue;
2. verifier V8 runs stages a and b, with no searchers and no stage c, 2 verifiers;
3. then the post-run pipeline and N2's gate and marks.

Every fragment counts as a candidate: level 4's top-20 cut does not apply.

**Reported:**
- the share of kept fragments that reach level 7, the false-novelty rate, with a binomial 95% interval;
- that share next to the 78;
- the level at which each fragment stopped, and which check stopped it.

**Budget:** 12 h in all. Fragment generation takes at most 2 h per structure, and the verifier run 6 h.

### A first statement across families (review C4)

**Single-cell hypothesis (SC), with ties.** ∘ occurs only in subterms u∘v with u and v free of ∘, and every law of T
is one of two kinds:
- **constraint:** its ∘-subterms are all the same pair (u, v), or the swapped pair (v, u) when T proves ∘ commutative;
- **tie:** the law is exactly u∘v = u′∘v′.

**Lemma.** Under SC, for every · on a finite set, the set of ∘ with (·, ∘) ⊨ T is a product over the classes of the
tie relation on cells. The tie relation is the equivalence generated by the instances of the tie laws, given ·. Each
class takes one value, from the intersection of its cells' allowed sets.
- **Lean:** the lemma is proved beside `lean/Duet/Delta.lean`, for the law grammar of order ≤ 4, without `decide`,
  with the axiom audit. Exploratory, with no deadline.
- **Empirical side:** an SC theory without ties has ρ = 1 in B3.

**Classification,** syntactic: the 170 of N1's level 6, and N2's level 6, get SC without ties, SC with ties, or
neither, for ∘ given · and for · given ∘.

**Hypothesis:**
- `1f430506` and `1238c063` are SC without ties.
- `3818b88f`, `de0c0cf3` and `71fd2cc6` are SC with ties.

A failure is reported, and narrows the lemma's reach.

## N2: N1 with the gate's gaps closed (written 28 Nov 2026, 07:50 UTC, before anything below is computed)

Post hoc, descriptive. It replaces nothing. N1, F1 and the funnel stay as they are, and the README keeps showing N1.
An external review of commit 279157e (code and tracked files only) listed six faults in how N1 and the funnel count.
We checked each against the code and `work/check/` before writing this entry (REPORT, "N2"). Five hold as stated. The
sixth, dedupe's silent skip, is a real code path, but at 279157e it skips 0 of the 318 candidates. N2 is N1 with
these faults corrected, computed on the same pool, the 318 candidates of `work/check/candidates.json` at 279157e.
Nothing here feeds the search.

**Corrections.**
- **C1, parameter disguises.** The gate reads `check/hidden_param_candidates.json` (`soup.hidden --param`) as well as
  `hidden_candidates.json`. A candidate marked `definitional` there is known. Checked: 4 N1-ranked candidates are
  marked (`ebb197cc`, `811b3500`, `e51eb8f1`, `7e9c798d`; N1 ranks 115, 107, 106 and 90).
- **C2, ledger identifications.** Full identifications from `notes/rediscovery.md`, fixed now:
  - `a9295908` (row 11, a fragment of Heyting algebras);
  - `71fd2cc6` (row 13, commutative g-dimonoids plus one law);
  - `69dfbd8e` (row 7, as N1 already has it).

  Each makes its whole N2 dedupe class known. Rows 6, 8 and 9 are partial and stay "related", as in N1. Row 12 is
  covered by C1. Checked: `a9295908` is N1 rank 10 and in level 7.
- **C3, a dedupe on the union corpus with three outcomes** (`soup.dedupe --union --out dedupe2`).
  - **Corpus:** the corpus is the union of every run directory in `soup.funnel.DIRS`.
  - **Pairs:** every unordered pair of candidates gets one of three outcomes over the 8 relabellings:
    - *equivalent*: E proves both directions for some relabelling. 20 s per direction, as N1.
    - *separated*: for every relabelling, a corpus structure satisfies one theory and fails a law of the other.
    - *unknown*: otherwise. Before a pair is called unknown, it gets a second pass on every relabelling that passed the
      model filter: E with 120 s per direction, then Vampire (`prove_vampire`, discount) with 120 s.
  - **Reporting:** the number of candidates with no model in the union corpus is printed, and they are reported as
    never compared. Level 5 is reported as a range:
    - upper bound: classes from the equivalent pairs only, as in N1;
    - lower bound: the classes when the unknown pairs are merged too.

  N2's "one per dedupe class" uses the equivalent pairs.
- **C4, undecided checks decided** (`soup.decide`, a new post hoc module). For every candidate that passes C1–C3's
  identification gate and carries a flag in N1:
  - **`split None` or `split not run`:**
    - **Finite certificate:** `soup.split.screen` on sizes 2–5, up to 3,000 Mace4 models per size and 300 s per size.
    - **Proof:** `prove_split` with the union corpus, 120 s per E call.
    - **Wall time:** 3,600 s per theory.
    - **Outcomes:** true, false or none.
  - **`R1 kind?` relations:**
    - every law the relation still lacks gets E for 300 s;
    - for every law E does not prove, Mace4 looks for a separating model on sizes 2–8 (600 s), then Vampire FMB
      (`-sa fmb`, 300 s), then `soup.linear` over its rings.
    - Outcomes: decided known (every law proved), decided not (a separating model, re-checked on its tables), or
      undecided.

  A decided known goes to the gate as known, and a decided not drops the flag. An undecided candidate stays in and
  is marked "undecided". Levels 6 and 7 are reported as decided plus undecided.
- **C5, a second prover.** Every claim E proved for a candidate that passes the gate is proved again: first
  `prove_vampire` (discount, 120 s), then `prove_twee` (120 s) for those Vampire does not prove.
  - In N2's "works" gate and its off-diagonal key, a claim counts as proved only when a second prover confirms it.
  - The unconfirmed claims are listed. None is called false unless a finite model refutes it.
  - Checked: 132 of the 477 claims that N1-ranked theories proved had no second prover (z3 was skipped after an E
    proof, V7 and later), in 54 theories.

**Order.** N1's six keys, unchanged, computed on the corrected inputs.

**Levels reported beside N1's,** for N1 and N2 side by side in REPORT: level 5 (N2 as a range), level 6 and level 7
(N2 as decided + undecided). Level 7 is N1's definition: an off-diagonal proved emergent law, no classical model, and
nothing related. Each item's changes are listed.

**Expectations (descriptive, not tests).**
- Level 6 loses at least the 4 parameter disguises and `a9295908`.
- Level 7 loses at least `a9295908`.
- How much more C3–C5 move is the open part.

**Code, tests and budget.**
- **Code:**
  - `soup/novelty2.py` writes `check/novelty2_ranking.json` and `notes/candidates_table_n2.md`. It reuses N1's
    helpers, and `soup/novelty.py` is not changed.
  - `soup/dedupe.py` gets `--union --out`; its default (N1) behaviour stays.
  - `soup/decide.py` and `soup/reprove.py` (C4 and C5).
- **Tests** (`tests/test_n2.py`): the three dedupe outcomes on toy theories, the level-5 range, the C1 and C2 gate
  additions, and an unconfirmed claim that does not count as proved.
- **Budget:**
  - Nothing runs beside a stream run; none is running.
  - At most 4 parallel prover jobs, with `podman stats` checked first.
  - Prover wall times as above; C4's wall time per theory caps the total.

**Caveats.**
- N2 is post hoc. Its corrections were chosen after seeing N1's output and a review of it.
- Its budgets are larger than N1's, so "decided" partly reflects more time, not a better method.
- The pool is still the top 20 per run by verified score (review item C1, a separate preregistration).

## X12: arm fusion6 against fusion5, run side by side (written 26 Nov 2026, 18:52 UTC, before X12 starts)

Confirmatory for the family pressure, exploratory for the rest. Arm `fusion6` adds pressure toward rare families (REPORT,
"Family pressure"). In a 15-minute live smoke run (REPORT, "fusion6 against fusion5"), the 80 theories its verifiers
would reach first spanned 53 F1 families against fusion5's 13, at cheap scores 41% lower. X12 asks whether that
diversity survives verification, and at what price in score. It is the first run since T4 with a matched control arm,
in answer to X11's main caveat. The user asked for X12 after the smoke run.

**Design.**
- **Two arms, side by side,** in two data directories, `x12-f5` (arm `fusion5`) and `x12-f6` (arm `fusion6`). Each is
  made by `soup.t4_setup --dir <dir>`, then x11's corpus is copied in (19,531 found structures), and
  `soup.known build --out /data/<dir>` gives 129 known entries, 1,893 candidate entries and 78,175 seen-before keys
  (the library rebuilt after X11, as in the smoke run). Queues and results start empty.
- **Verifier V7, stages a and b only.** `--drain-c` equals the block's budget, so no verifier starts a stage-c task
  (`supervisor.c_until`; stage c settled 3 of about 28 claims in X11). Claims stage b leaves open wait in each
  directory's stage-c lane. Scores are stage-b scores.
- **Processes, per arm:** 2 searchers kept alive (`--min-searchers 2`), 2 verifiers, `--recycle-mb 700`,
  `--mem-stop-mb 1000`. Both arms together use 8 processes, as X11 did. The push gate is unchanged (`--gate 0.5`).
- **Image:** `soup:x12` = `62d4e04a6c98`, built from `158bb3d`, which is X11's code plus documentation (110 tests pass).
- **Budget and blocks:** 28,800 s per arm, in one or more blocks of at least 2 hours each, chosen by the user at the
  start. Both arms run each block at the same time, started within one minute of each other, with the same
  `--budget`. Block k uses `--run x12f5<letter>` and `--run x12f6<letter>`, and `--seed0` 1801 + 50(k − 1) in both
  arms. If one arm's memory rule stops it, the other arm is stopped by hand within 5 minutes, and the next block gives
  both the same remaining budget. Nothing in either directory is changed by hand between blocks. X12 ends by
  3 Dec 2026 (UTC) with what has run.
- **Before each block:** compare `date -u` with `podman machine ssh date -u`, check that no other soup container
  runs, check the user's containers' memory with `podman stats --no-stream`, and keep the Mac awake.
- **Command** (block k, arm a in {5, 6}, budget B):
  `podman run -d --name soup-x12f<a><letter> -v "$PWD/work:/data" -e SOUP_DATA=/data/x12-f<a> -e SOUP_VERIFIER=V7
  soup:x12 python3 -m soup.stream.supervisor --arm fusion<a> --searchers 2 --verifiers 2 --min-searchers 2
  --drain-c B --seed0 <1801 + 50(k-1)> --budget B --recycle-mb 700 --mem-stop-mb 1000 --run x12f<a><letter>`.

**Done before this entry, disclosed.**
- X11's results and its post-run checks were all read, and so was the push-gate measurement (`notes/push_gate.out`).
  X11 made 99% of its pushes in its first 805 s.
- The offline prototype (`notes/family_sim.out`) and the paired smoke run (`notes/fusion6_smoke.out`) were read. The
  smoke run used this library and corpus, 4 searchers and 1 verifier per arm, for 900 s, and its copies were deleted.
  The predictions below are informed by it.

**Predictions.** Each is judged on the sum over blocks. F1 labels come from `soup.taxonomy build --confirm` with both
directories added to `taxonomy.RUNS`. "Structured" and "family" are F1's.
- **Y1, diversity (primary):** at equal sample size, fusion6's structured verified theories span at least 1.5 times as
  many families as fusion5's. Equal size means the expected number of distinct families in a random subsample of m
  theories without replacement, m the smaller arm's number of structured theories (exact rarefaction:
  E = Σ_f [1 − C(N − n_f, m) / C(N, m)]).
- **Y2, concentration:** the largest family's share of structured theories in fusion6 is at most half of fusion5's.
- **Y3, quality (non-inferiority, the open question):** fusion6's share of verified theories with a positive score is
  at least 0.8 times fusion5's. Fisher's exact test (two-sided) on the 2 × 2 table is reported beside it.
- **Y4, candidates:** among each arm's 20 candidates (the top 20 non-fragments), fusion6 has at least as many
  disconnected ones (`notes/disconnected.py x12-f6 x12-f5`), and at least as many at funnel level 7.
- **Y5, new families:** fusion6 adds more new structured families than fusion5. New means that no theory of any run up
  to X11 has it; the other arm does not count.
- **Y6, cost:** fusion6's searchers make at least 0.5M evaluations per searcher-hour (smoke 0.69M). Its rescores and
  the parameter skip's Mace4 step together take at most 15% of its searcher time (smoke 8.9%).
- **Y7, the gate (descriptive):** in both arms, 99% of the first block's pushes come within its first 10%
  (`notes/push_gate.py`).
- **Y8, the run:** no block is stopped by a memory rule, and each arm verifies at least 300 theories.

**After the run:**
- X11's post-run pipeline on both directories, with `x12-f5` and `x12-f6` added to `taxonomy.RUNS`, `funnel.DIRS` and
  `known.RUN_DIRS`, in that order: fragments, statistics, candidates (both as sources), profile `--jobs 4`, hidden
  and `--param`, relabel, rank, rediscover, the split per candidate, `notes/disconnected.py x12-f6 x12-f5`, dedupe,
  N1, F1, the funnel and the linear sweep.
- A script `notes/x12_predictions.py`, written after the run with the definitions above, judges Y1–Y8. Then a REPORT
  section.

**Caveats.**
- **Family diversity is partly built in.** fusion6 is designed to push diverse families, so Y1 and Y2 are expected.
  The informative predictions are Y3 and Y4: whether those theories hold up once verified.
- **Same seeds do not make paired trajectories.** The arms diverge at the first proposal. Each arm is one realisation,
  and two searchers per arm are a small sample of search trajectories.
- **The push gate is unchanged.** Both arms will verify mostly what they pushed in their first minutes (Y7), so the
  comparison is between the heads of two queues, not between whole searches.
- **Shared machine.** Both arms share the VM's CPU and memory, and the user's containers. Contention hits both arms
  alike, since they run at the same time, but it is not controlled.
- **No stage c.** Claims left open by stage b stay open, so scores are stage-b scores. That is the same for both arms.
- **F1 labels rest on corpus models.** E confirmed about 97% of the properties so far. Each arm's corpus also grows
  with its own countermodels, and F1 labels every run on one union corpus.
- **A sleeping Mac** freezes the VM, and the budget then runs on a frozen clock. That would be a deviation.

## X11: arm fusion5, the parameter-disguise skip at scale (written 26 Nov 2026, 06:17 UTC, before X11 starts)

Exploratory and descriptive. Half of X10's 578 verified theories were parameter disguises of one shape (REPORT, "X10").
Arm `fusion5` skips them in the search (`70ba826`; REPORT, "A search-side skip for parameter disguises"). X11 asks what
the search finds once they are skipped. The user chose X11 before the stage-c backlog and before an ML ranking.

**Design.**
- **Data directory:** `x11`. `soup.t4_setup --dir x11`, then x10's corpus is copied in (17,341 found structures), and
  `soup.known build --out /data/x11` gives 129 known entries, 1,733 candidate entries and 74,884 seen-before keys. The
  queue and the results start empty. X10's 207 stage-c tasks are not copied.
- **Arm and verifier:** arm `fusion5`, verifier V7. The image is `c96838c1e261`, built from `70ba826`.
- **Processes:** as in x10b: 4 searchers kept alive (`--min-searchers 4`), 4 verifiers, `--max-c 2 --cap-c 2`,
  `--drain-c 3600`, `--recycle-mb 700`, `--mem-stop-mb 1000`. The pending lane is capped at 1,500.
- **Budget and blocks:** 28,800 s in all, in one or more blocks. Each block is at least 2 hours and at most what is
  left, chosen by the user at its start; the last block takes what is left. Block k uses `--run x11<letter>`,
  `--seed0` 1601 + 50(k − 1) and `--budget` the block's length. Nothing in `work/x11` is changed by hand between
  blocks, and the image stays the same. If the 28,800 s are not used by the end of 30 Nov 2026 (UTC), X11 ends with what
  has run.
- **Before each block:** compare `date -u` with `podman machine ssh date -u`, check that no other soup container runs,
  check the user's containers' memory with `podman stats --no-stream`, and keep the Mac awake for the block.
- **Command** (block k):
  `podman run -d --name soup-x11<letter> -v "$PWD/work:/data" -e SOUP_DATA=/data/x11 -e SOUP_VERIFIER=V7 soup python3 -m
  soup.stream.supervisor --arm fusion5 --searchers 4 --verifiers 4 --min-searchers 4 --max-c 2 --cap-c 2 --drain-c
  3600 --seed0 <1601 + 50(k-1)> --budget <block> --recycle-mb 700 --mem-stop-mb 1000 --run x11<letter>`.
- **Amendment before the start (written 26 Nov 2026, 07:58 UTC):** after this entry, the `soup` image was rebuilt for
  an offline prototype (arm `fusion6`, which X11 does not use). So the command names the preregistered image by a tag,
  `soup:x11` = `c96838c1e261`, in place of `soup`. Nothing else changes.

**Done before this entry, disclosed.**
- X10's results, its post-run checks and its REPORT section were all read.
- `soup.paramskip` was measured on every result of X5 to X10 (`notes/paramskip_check.out`). It skips all 711 theories
  V6 marked, no theory at funnel level 7 or 8, and 22 of 258 candidates (15 known, 7 at N1 ranks 63–84 with
  classical models). 34 of its skips are false (E refutes).
- Paired smoke runs of 600 s, `fusion4` against `fusion5`, on copies of x10's corpus with this library, were deleted
  afterwards (`notes/paramskip_smoke.out`). Evaluations per searcher-hour were 0.91M and 0.90M. Pushed disguises
  numbered 31 of 1,548 under fusion4 and 0 of 1,550 under fusion5. Of the verified theories, 48 and 50, none was a
  disguise.

**Predictions** (descriptive; on the sum over blocks; X10 = its own 578 theories, or the whole `x10` directory for F1):
- **W1, the skip:** at most 5% of X11's verified theories are marked "parameter definition" by V6 (X10: 50.9%).
- **W2, its cost:** the searchers make at least 0.75M evaluations per searcher-hour (x10b 0.90M), and the Mace4 step
  takes at most 5% of searcher time (smoke 1.2%).
- **W3, structure:** F1's structured family is at least 30% of `x11` (X10 11.0%, X9 61.4%, X8 + x8b 43.2%).
- **W4, the 𝔽₄ corner:** at most 10 of X11's 20 candidates have a classical model among the base probes (X10 15).
- **W5, disconnected:** at least 8 of X11's 20 candidates are disconnected (X10 4, X9 14, X8 9).
- **W6, families:** X11 adds at least 5 new structured families (X10 3).
- **W7, memory:** no block is stopped by its memory rule.

**After the run:** X10's post-run pipeline with `x11` added to `taxonomy.RUNS`, `funnel.DIRS` and `known.RUN_DIRS`:
fragments, statistics, candidates, profile `--jobs 4`, hidden and `--param`, relabel, rank, rediscover, the split per
candidate, `notes/disconnected.py x11 x10`, dedupe, N1, F1, the funnel, the linear sweep and a REPORT section. The
predictions are judged by a script `notes/x11_predictions.py`, written after the run, using the definitions above.

**Caveats.**
- **No control arm.** The comparison with X10 is confounded: the library rebuilt after X10 already skips X10's
  disguises and its candidates' equivalents, and under fusion4 the smoke pushed only 2% disguises. The smoke is the only
  within-library contrast, and it lasted 10 minutes.
- **False skips:** about 3.5% of the skips measured on X6–X10 are wrong, and their countermodels have more than 4
  elements. The skip may also push the search into a disguise it does not test, such as terms in which x or y occurs
  twice. Such terms are not in the skip's list, and V6 would still catch them in the verifier.
- **Countermodels from the searchers** go into the corpus, and so change the cheap scores of other theories. The
  verifiers' models do the same.
- **A sleeping Mac** freezes the VM, and the budget then runs on a frozen clock. That would be a deviation.

## X10: stage c under a cap, with the search beside it (written 25 Nov 2026, 06:03 UTC, before X10 starts)

Exploratory and descriptive. X9 left 156 stage-c tasks and showed two gaps (deviation 11). Both are fixed:
`--cap-c` and the drain rule (`f9a774e`), and `--max-c` (`3e7394b`); see REPORT, "The stage-c cap and the drain rule".
The user chose an 8-hour night run with the search beside stage c over a full drain, which would take about 33 hours.

**What stage c has done so far** (`notes/stagec_history.py`, output `notes/stagec_history.out`):
- Since T4 it settled about 7 of the 96 claims it ran on (7.3%), all by Vampire FMB, and proved none. Since X5, when FMB
  entered stage c, the figure is 7 of 52 (13.5%). The mean is 37.7 minutes per theory over all runs.
- The 156 tasks hold 221 unknown claims: 6 tasks have none left, 85 have one, 59 two and 6 three. Their priorities run
  from 12.8 to 25.0, and none is a candidate or in N1.
- So the run is not expected to change a candidate. It measures stage c under a cap, and it continues the search.

**Design.**
- **Data directory:** `x10`, a fork of X9's state, made this morning so that the smoke runs could copy it. x9 has not
  changed since.
  - `soup.t4_setup --dir x10`, then its corpus is replaced by a copy of X9's (16,826 files);
  - X9's `queue/stage2c` (156), `queue/pending` (1) and `queue/seen` (18,333) are copied in;
  - so are the 156 stage-b results that the stage-c tasks read, and nothing else from `results/`;
  - `soup.known build --out /data/x10`: 51 known entries, 1,651 candidate entries, 62,038 seen-before keys.
- **Arm and verifier:** arm `fusion4`, verifier V7, as in X9.
- **Processes:** 6 searchers kept alive (`--min-searchers 6`) and 4 verifiers.
  - `--max-c 2 --cap-c 2`: two stage-c tasks whenever the lane has work, never more. v0 prefers stage c, one more
    verifier joins it there, and the other two work on stages a and b.
  - The verifier floor is then 3, so the rebalancer can move one verifier to search if pending runs dry.
  - The pending lane is capped at 1,500 (the default `--qmax`).
- **Memory:** `--recycle-mb 700`, `--mem-stop-mb 1000`. MemAvailable is now logged every tick.
- **Budget and seeds:** 28,800 s (8 h); seeds from 1401.

**Run:**
1. Compare `date -u` with `podman machine ssh date -u`, and keep the Mac awake for the whole budget (the app's
   keep-awake).
2. `podman run -d --name soup-x10 -v "$PWD/work:/data" -e SOUP_DATA=/data/x10 -e SOUP_VERIFIER=V7 soup python3 -m
   soup.stream.supervisor --arm fusion4 --searchers 6 --verifiers 4 --min-searchers 6 --max-c 2 --cap-c 2 --seed0 1401
   --budget 28800 --recycle-mb 700 --mem-stop-mb 1000 --run x10`.

**Done before this entry, disclosed.**
- **Code:**
  - `--cap-c`, the drain rule and the fresh-heartbeat check (`f9a774e`);
  - `--max-c` and the MemAvailable log (`3e7394b`);
  - 101 tests pass.
- **Smoke runs** on copies of the fork, deleted afterwards (`notes/capsmoke.py`):
  - `capsmoke`: 5 verifiers, no searcher, cap 2 (REPORT).
  - 6 searchers, 5 verifiers, `--max-c 3 --cap-c 3` (`notes/x10smoke_cap3.out`): the memory rule fired after 217 s
    (860 MB). The three stage-c tasks started together, and their long E runs grew at the same time. That was the first
    design, dropped.
  - 6 searchers, 4 verifiers, `--max-c 2 --cap-c 2` (`notes/x10smoke_cap2.out`): ran its 900 s.
    - MemAvailable fell to 2,516 MB while both E runs grew, then stayed near 5.6 GB.
    - 22 theories were verified, about 44 per stage-a/b verifier-hour.
    - 426,187 evaluations were made, 0.28M per searcher-hour at a steady rate. X8 + x8b made about 0.72M; X9's corpus is
      about twice X8's.
    - The pending lane reached 1,500 in 4 minutes.
  - Nothing else was read.

**Predictions** (descriptive):
- **U1, the cap:** no tick in `logs/stats.jsonl` has more than 2 workers in stage c, and the run reaches its budget
  without the memory rule.
- **U2, stage-c throughput:** at least 12 of the 150 copied tasks with open claims get through stage c. Two slots over
  8 h at 40 minutes would be 24; under load X8 took 71 minutes.
- **U3, stage-c yield:** stage c settles at least 5% of the claims it runs on, and proves at most one. Since T4 it has
  settled 7.3% and proved none.
- **U4, the search:** level 0 rises by at least 10M, to at least 125.1M. The smoke rate gives about 13M for 48
  searcher-hours. Restated in the amendment below.
- **U5, verification beside stage c:** at least 400 new theories get through stages a and b (the smoke rate gives about
  700).

**Amendment (written 25 Nov 2026, 08:02 UTC, before X10 starts).**
- **Code since this entry:** the column cache in `Corpus.has` (`74a07ff`; REPORT, "Why the searchers slowed down"). It
  changes the searchers' speed only: on 3,000 replayed proposals their outputs are byte-identical. X10 runs with it.
- **A second smoke run** with X10's exact command, 900 s on a fresh copy of the fork, deleted afterwards
  (`notes/smoke_rate.py` and `notes/capsmoke.py`, output `notes/x10smoke_cache.out`):
  - 0.60M evaluations per searcher-hour, against 0.28M in the cap-2 smoke, measured the same way (from the first tick
    with evaluations to the last live tick);
  - stage c peaked at 2 tasks, and MemAvailable fell to 2,133 MB at 333 s (the cap-2 smoke: 2,516 MB);
  - only 7 theories got through stages a and b (the cap-2 smoke: 22). One of the two stage-a/b verifiers spent 850 s on
    one theory in stage b, and two parameter screens took about 170 s each with E unknown.
- **U4, restated:** level 0 rises by at least 22M, to at least 137.1M. The new rate gives about 29M for 48
  searcher-hours, and the threshold keeps the old margin (10M of 13M). The rate will fall as the corpus grows.
- **U5 is kept at 400.** The two smokes give 14 and 44 theories per stage-a/b verifier-hour, so 220 to 700 over the
  run: U5 is less likely to hold than when it was written.
- Nothing else changes.

**Second amendment: X10 in blocks (written 25 Nov 2026, 13:48 UTC, before X10 starts).** The user asked to run X10 in
shorter blocks instead of one 8-hour run, so the Mac has to stay awake for one block at a time.
- **Code since the first amendment:** `--drain-c S` (`921f19e`; REPORT, "The stage-c drain"). In a block's last S
  seconds no verifier starts a stage-c task, and the journal's end entry counts the stage-c tasks the stop cut. 103 tests
  pass. A 300 s check run on a copy of the fork (`notes/x10drain_check.out`) drained at 101 s and reported 2 cut.
- **Blocks:** X10 is a sequence of blocks in `work/x10` whose budgets add up to the preregistered 28,800 s.
  - Each block is at least 2 hours and at most 4, chosen at its start; the last block takes what is left, however short.
  - Block k runs X10's command with `--run x10<letter>` (x10a, x10b, ...), `--seed0` 1401 + 50(k - 1), `--budget` the
    block's length and `--drain-c 3600`. Everything else is as above.
  - Before each block: compare the clocks, check that no other soup container is running, and keep the Mac awake for
    the block.
  - Between blocks nothing in `work/x10` is changed by hand: no known-library rebuild and no new image. The image is
    the one built from `921f19e`.
  - If the blocks have not used the 28,800 s by the end of 28 Nov 2026 (UTC), X10 ends with what has run, and the
    predictions are judged on that.
- **What a block boundary costs:**
  - Each block's searchers start from empty archives, so the search does not build on the elites of the block before.
  - Stage-c tasks still running at a stop start over in the next block. The drain limits this to tasks longer than an
    hour. Since X5, stage-c tasks took a median of 33 minutes and at most 61 without much load, and a median of 79 under
    X8's load (`notes/stagec_history.out`), so some will be cut. Each block's journal gives the count.
- **The predictions** U1-U5 are judged on the sum over all blocks, with U4 as restated. Stage c starts tasks only in
  the first B - 1 hours of a block of B hours, so U2 is less likely to hold than in one 8-hour run.
- **A memory stop or a sleeping Mac** in a block is a deviation. The block's elapsed time counts toward the 28,800 s,
  and the next block may still run.
- **After the run:** the post-run steps treat every x10* run in `work/x10` as X10. The funnel sums per run inside a
  directory, and the families are assigned per directory.

**Third amendment: 4 searchers while the user's stack runs (written 25 Nov 2026, 16:23 UTC, before X10's second block
starts).** After deviation 12 the user chose to keep their web stack running during the blocks, so the blocks have to
give up the memory the stack takes.
- **Measured** (x10a's `logs/stats.jsonl`, and the VM at 16:21 UTC with no soup container running):
  - a searcher's PSS had a median of 476 MB and a maximum of 589 MB;
  - the stack holds about 1.2 GB (`podman stats`), and its frontend uses a fifth to a quarter of a core;
  - with every container of the user's running and no soup container, the VM has 10,040 MB available of 11,917.
- **The change:** from x10b on, blocks run with `--searchers 4 --min-searchers 4`. Two searchers free about 1.0-1.2 GB,
  about what the stack takes, and two cores. Everything else stays as in the second amendment: 4 verifiers,
  `--max-c 2 --cap-c 2`, the prover and z3 memory caps, the image, the seed rule. Verification is unchanged; only the
  search gets fewer hours.
- **Why not the alternatives:**
  - A lower prover or z3 cap would change which claims get settled, so stage c's yield (U3) would no longer be
    measured with V7 as in X9 and x10a.
  - One stage-c slot instead of two would halve U2's throughput.
  - A lower memory rule would let the VM come closer to killing processes, the user's among them.
- **What it does not fix:** worker PSS counts each worker's own process only; E, Vampire and Mace4 run as child
  processes outside it. In x10a the memory outside the workers ranged from about 2.0 to 5.6 GB as those children came
  and went. With 4 searchers the low point at x10a's stop would have been about 1.5 GB (an estimate). A z3 peak in a
  stage-a/b verifier together with E peaks in both stage-c verifiers could still trip the rule; that would be a
  deviation, as before.
- **U4 is kept as written** (at least 22M) and is now expected to fail: x10a's 1.68M plus 29.4 searcher-hours at
  0.45-0.60M per searcher-hour gives about 15-19M. U1 failed in x10a (deviation 12). U2, U3 and U5 are unchanged.

**Fourth amendment: the rest of X10 as one block (written 25 Nov 2026, 18:42 UTC, before x10b starts).** The user
chose to run what is left of X10 as one block instead of two.
- **x10b** gets `--budget 26487`, the 28,800 s less x10a's 2,313 s. This lifts the second amendment's 4-hour cap for
  this block only. Everything else is as in the second and third amendments: run id `x10b`, `--seed0 1451`,
  `--drain-c 3600`, 4 searchers.
- **Why:** one block boundary fewer.
  - Stage c can start tasks for 22,887 s, against 19,287 s in a 4-hour block followed by a 3.4-hour one.
  - The searchers keep their archives for the whole block.
  - No stage-c task is cut at a boundary in between.
- **Cost:** the Mac stays awake for about 7.4 h with the user's stack beside the run, so the memory rule has a longer
  window to fire in. A stop is a deviation. The time that ran counts, and if any budget is left, one more block may run
  before the end of 28 Nov 2026 (UTC) with what is left.
- **Clocks:** at 18:41 UTC the VM was 2,691 s behind the Mac, after the Mac had slept. x10b starts only once the two
  clocks agree, so that no wall-time deadline is caught by a later jump of the VM's clock.
- **Command:** `podman run -d --name soup-x10b -v "$PWD/work:/data" -e SOUP_DATA=/data/x10 -e SOUP_VERIFIER=V7 soup
  python3 -m soup.stream.supervisor --arm fusion4 --searchers 4 --verifiers 4 --min-searchers 4 --max-c 2 --cap-c 2
  --drain-c 3600 --seed0 1451 --budget 26487 --recycle-mb 700 --mem-stop-mb 1000 --run x10b`.

**After the run:**
- X9's post-run pipeline with x10 added (`taxonomy.RUNS`, `funnel.DIRS`, `known.RUN_DIRS`): the split per candidate,
  dedupe, N1, F1, the funnel, the linear sweep and a REPORT section.
- The 156 copied results are reported apart, since their stages a and b ran in x8, x8b or x9.

**Caveats.**
- **Double counting:** level 1 and F1 count the copied results under both x9 and x10, as with the 65 in X9. The distinct
  count is reported.
- **Wall time under load:** E's limits are CPU time, but those of FMB, Mace4 and the linear screen are wall time, and
  10 processes on 11 cores slow them down.
- **The lane is ordered by priority:** the highest-priority tasks will be done and most of the rest will not.
- **A sleeping Mac:** if it sleeps, the VM freezes and the budget runs on a frozen clock (24 Nov). That would be a
  deviation.

## X9: verifier V7 drains X8's queue (written 24 Nov 2026, 22:27 UTC, before X9 starts)

Exploratory and descriptive. X8 + x8b were search-heavy (8 searchers, 3 verifiers), and verification was the bottleneck:
444 verified in 9 hours, with 1,256 theories and 65 stage-c tasks left in the queue (REPORT, "X8 + x8b"). The user chose
a run that works through that queue with a faster verifier, starting tonight.

**Verifier V7** (`soup/verify.py`) = V6 plus two changes, both measured on X8 + x8b:
- **No z3 after an E proof** (`z3_after_e=False`). Since V2 a claim's difficulty is E's proof length; the z3 run on a
  claim E had proved only kept the z3 effort comparable with old runs. On X8 + x8b z3 hit its cap on 113 of 269
  E-proved claims, and the 86 theories with such a claim took 4.2 of stage b's 11.3 hours. Scores do not change.
- **Linear models** (`soup.linear`) for each claim E neither proves nor saturates:
  - in stage b, after E's small run and before FMB, on rings up to 32 elements and affine models up to 9, 60 s;
  - in stage c, before FMB and Mace4, on the full range (rings up to 64, affine up to 16), 600 s;
  - a model counts only after `check_offline.check_finite` accepts it, and it goes into the corpus;
  - the post-run sweep refuted 14 of X8's 116 open claims this way, all linear, on 8 to 17 elements.

**Design.**
- **Data directory:** `x9`, a fork of X8's state:
  - `soup.t4_setup --dir x9`, then its corpus is replaced by a copy of X8's (7,708 structures);
  - X8's `queue/pending` (1,256), `queue/stage2c` (65) and `queue/seen` (18,333) are copied in;
  - so are the 65 stage-b results that the stage-c tasks read, and nothing else from `results/`;
  - `soup.known build --out /data/x9` then includes X8's candidates and seen keys (62,038).
- **Arm and verifier:** arm `fusion4`, verifier V7.
- **Processes:** 7 verifiers and no searcher at the start.
  - The rebalancer starts searchers only from idle verifiers, as in every run, so the search resumes once the queue
    runs low.
  - The pending lane is capped at 5,000 (`--qmax 5000`), so no copied task is trimmed.
- **Memory:** `--recycle-mb 700`, `--mem-stop-mb 1000`.
- **Budget and seeds:** 28,800 s (8 h); searchers started by the rebalancer get seeds from 1301.

**Run:**
1. the fork (`t4_setup`, copies, `soup.known build`), as above;
2. `podman run -d --name soup-x9 -v "$PWD/work:/data" -e SOUP_DATA=/data/x9 -e SOUP_VERIFIER=V7 soup python3 -m
   soup.stream.supervisor --arm fusion4 --searchers 0 --verifiers 7 --seed0 1301 --budget 28800 --qmax 5000
   --recycle-mb 700 --mem-stop-mb 1000 --run x9`.

**Done before this entry, disclosed.**
- **Code:** V7, with `tests/test_v7.py`; 96 tests pass.
- **Benchmark of stage b** (`notes/v7_bench.py`, output `notes/v7_bench.out`):
  - V6 against V7 on 24 X8 theories with their recorded stage-a output: 12 with a z3-capped E proof, 12 with a hard
    claim, seed 9, from theories whose stage b took at most 600 s.
  - V7 took 600 s against V6's 1,424 (58% less). 5 claims changed outcome, all to a linear refutation: three
    from unknown, two from an FMB refutation. No score changed.
  - A first version searched the full range in stage b: 21% less, with up to 60 s added per hard claim. That is why
    stage b now stops at 32 elements.
- **Smoke runs** on forks of X8's state, 4–6 minutes each, all deleted afterwards:
  - 10 verifiers and 1 searcher: the stage-c tasks were dropped, because their stage-b results had not been copied. Hence
    the results copy above.
  - With the results copied, 10 and 8 verifiers both tripped the memory rule (911 and 966 MB available) once two
    stage-c tasks ran together, with prover processes capped at 2 GB each.
  - 7 verifiers and no searcher (one stage-c task at a time): at least 6.4 GB stayed available; 57 verified in 6
    minutes, and the copied pending lane fell from 1,256 to 1,199.
  - With 1 searcher, about 200 new theories were pushed in 4 minutes, enough to crowd out the copied ones; hence no
    searcher at the start.
  - Nothing else was read.

**Predictions** (descriptive):
- **S1, throughput:** at least 25 theories through stages a and b per verifier-hour, 1.5 times x8b's 16.9 (397 in
  3 × 7.85 h). Verifier-hours are the time integral of the live verifier count in `logs/stats.jsonl`.
- **S2, stage c:** a mean of at most 35 minutes per theory through stage c, half of x8b's 70.6 (8.24 h for 7).
- **S3, the linear screen:** it refutes at least 5% of the claims it runs on in stage b.
- **S4, the queue:** at least 1,000 of the 1,256 copied pending theories get a result.

**After the run:** X7's post-run pipeline with x9 added (`taxonomy.RUNS`, `funnel.DIRS`, `known.RUN_DIRS`), the split per
candidate, dedupe, N1, F1, the funnel and a REPORT section. The 65 copied stage-b results are reported apart: their
stages a and b ran in x8b under V6.

**Caveats.**
- The copied queue is what X8's verifiers had not reached, after trimming by priority. So the comparison with x8b is
  not randomized, and the hardest stage-c tasks may be among the copied ones.
- Seven verifiers load the machine more than three did. E's limits are CPU time, but FMB's and the linear screen's are
  wall time.
- The theories were found by X8's searchers but are verified in x9, so F1 counts them under x9.
- One stage-c task at a time: most of the 65 stage-c tasks will not be reached.

## X8: search-heavy, toward 100M (written 24 Nov 2026, 08:03 UTC, before X8 starts)

Exploratory and descriptive. The user's aim (24 Nov), in their words: 50M is "the dust removed", 100M "the surface
scratched", 200M "digging". They chose a search-heavy run.
- **Level 0:** the corrected funnel count, raw, with distinct beside it: 63,662,919 before X8.
- **Why search-heavy:** in X5–X7 the rebalancer cut 4 searchers to 1 within 30 minutes.

**Design.**
- **Arm and verifier:** arm `fusion4` with verifier V6, as in X7.
- **Library:** the known library and the seen-before keys are rebuilt with `soup.known build --out /data/x8`, so
  they include X7.
- **Processes:** 8 searchers and 3 verifiers. `--min-searchers 8` means the rebalancer never retires a searcher.
  It can still turn an idle verifier into a searcher, keeping at least 2 verifiers.
- **Memory:** verifiers recycle above 700 MB private (`--recycle-mb 700`), and the run stops below 1,000 MB available
  (`--mem-stop-mb 1000`).
- **Budget and seeds:** 32,400 s (9 h), seeds 1201–1208.

**Run:**
1. `python -m soup.t4_setup --dir x8`;
2. `soup.known build --out /data/x8`;
3. `podman run -d --name soup-x8 -v "$PWD/work:/data" -e SOUP_DATA=/data/x8 -e SOUP_VERIFIER=V6 soup python3 -m
   soup.stream.supervisor --arm fusion4 --searchers 8 --verifiers 3 --min-searchers 8 --seed0 1201 --budget 32400
   --recycle-mb 700 --mem-stop-mb 1000 --run x8`.

**Done before this entry, disclosed.**
- `--min-searchers` was added to the supervisor, with a test. 86 tests pass.
- `soup.known` now also reads x4a and X7 for the seen-before keys, which number 43,705 (X7 had 38,701). Before this
  fix, X7's own theories would not have been skipped.
- A 4-minute engineering smoke run (`work/x8smoke`, seeds 1991–1998, deleted afterwards):
  - the 8 searchers stayed alive with no rebalancing;
  - they made 719,100 evaluations (about 10.8M per hour at the start, on the small starting corpus), of which each
    searcher counted about 83% as distinct;
  - 309–356 MB PSS per searcher, and 10.4 GB still available at the end;
  - 15 theories verified. Nothing else was read.

**Predictions** (descriptive):
- **R1:** the raw funnel level 0 passes 100M, so X8 adds at least 36.4M.
- **R2:** distinct evaluations are at least 70% of X8's raw ones (X7: 73.8%).
- **R3:** the parameter screen fires on less than 5% of X8's verified theories (X7: 2.2%).
- **R4:** F1, recomputed with X8, gives X8 at least one new structured family that holds at least 2% of X8's
  verified theories.

**After the run:** X7's post-run pipeline with x8 added (split per candidate, merged into
`check/split_candidates.json`). Then F1 (`soup.taxonomy build --confirm`, `report`), the funnel and a REPORT section.

**Caveats.**
- With 3 verifiers, most pushed theories are never verified. The queue is trimmed to 1,500 by priority, so the
  verified ones are the searchers' best.
- Evaluations get slower as the corpus grows. With fewer verifiers the corpus grows more slowly, which works the
  other way.

## F1: families of verified theories, and emerging patterns (post hoc; written 24 Nov 2026, 07:41 UTC, before it is computed)

Descriptive. The user's request (24 Nov): a statistic of families and their percentages next to the funnel, and the
emerging patterns. Code: `soup/taxonomy.py`. Data: every verified theory (`results/*.json` with laws) in the run
directories of the funnel. x4a's results are left out, as in the funnel. Percentages are per run directory, over all
of its verified theories.

**Primary family**, the first rule that matches, so the shares sum to 100% per run:
1. **Disguise:** stage a screened it (`screened`: split, division or parameter definition; V4 on).
2. **Known:** `check/rediscover.json` relates it to a catalogue entry, under some relabelling, as a fragment,
   subvariety or equivalent, proved by E. The model-only kinds ("subvariety?") do not count. Its key is also known
   if the ledger `notes/rediscovery.md` identifies it. The subtype is the catalogue entry, the first in catalogue
   order.
3. **No synergy:** no proved emergent law.
4. **Diagonal:** a proved emergent law in one variable (`offdiag.ONEVAR`).
5. **Argument-ignoring:** on the corpus it implies an `offdiag.IGNORE` law (X4's attractor).
6. **Structured:** everything else, labelled by its reduct signature.

A rule for square-ignoring laws (`IGNORE2`) was considered and dropped before this entry: every totally symmetric
quasigroup satisfies x·(x·x) = y·(x·y), so the rule would file classical structure as an attractor.

**Reduct signature.** Eleven properties of one operation, written for ·:
- commutative x·y = y·x; associative; idempotent x·x = x; constant squares x·x = y·y;
- squares are right identities x·(y·y) = x, and left identities (y·y)·x = x;
- left involutive x·(x·y) = y, and right involutive (y·x)·x = y;
- flexible x·(y·x) = (x·y)·x; x·(y·z) = x·y, and its mirror (x·y)·z = y·z.

With the same eleven for ∘, that is 22 laws, a set closed under the 8 relabellings.
- A theory has a property when the law holds in every model of the theory in the union of all runs' corpora.
- The signature lists the properties of · and of ∘. "TSQ" abbreviates commutative and left involutive.
- The family label is the least label over the 8 relabellings, so relabelled twins share a family.
- Evidence: for structured theories, E is asked for each property the corpus gives (10 s, 200,000 processed
  clauses). The confirmation rate is reported, and an unconfirmed property is marked model-implied.

**Emerging patterns.** Runs in time order: root, t4-prior, t4-noprior, x1, …, x7.
- A structured family is **new** in a run if no earlier run has a theory in it.
- It is **emerging** in a run if it has at least 10 theories there and its share there is at least twice its share in
  all earlier runs together.
- The same two flags are applied to proved emergent laws, each taken up to the 8 relabellings.
- **The accumulation curve:** distinct structured families against cumulative verified theories, and at each run's
  end against cumulative level 0. Chao1 (S + f1²/(2 f2), with f1 and f2 the families seen once and twice) estimates
  how many exist in total.

**Predictions:**
- **F1a:** in X7, "structured" is the largest primary family, and in T4 (t4-prior and t4-noprior together) its share
  is under 10%.
- **F1b:** at least 10% of the structured families seen up to X7 are new in X7.

**Caveats.**
- Corpus implication over-approximates real implication, so a signature can be too rich. The E confirmation
  bounds this error.
- A fixed list of 11 properties names only what it lists. Two theories in one family can still differ a lot.
- The "known" rule relies on our catalogue, not on the literature.

## X7: skip what is already known, a night run (written 23 Nov 2026, 19:46 UTC, before X7 starts)

Exploratory and descriptive. The user's instruction (23 Nov): "skip the already known, do not risk to do again the
same", and a new level-0 measurement.

**Design.** Arm `fusion4` is X6's `fusion2` plus three changes (`soup/known.py`, `soup/stream/searcher.py`). The
verifier is V6, as in X6.

1. **Known-library skip.**
   - Built once before the run by `python -m soup.known build --out /data/x7`, from the shared data and the ledger.
   - The library, each entry under all 8 relabellings:
     - 129 known entries: the 13 catalogue entries, which include the 10 named theories, and the 15 candidates
       identified in the ledger;
     - 1,097 entries for the other earlier candidates.
   - A theory is skipped if, on the corpus, it is a fragment or a subvariety of a known entry, or equivalent to an
     earlier candidate.
   - A strengthening of an unidentified candidate is not skipped: it is new ground.
   - The library's corpus view is rebuilt every 30 minutes.
2. **Seen-before skip.** The 38,701 theory keys that earlier runs pushed or verified (`seen_before.json`) are never
   inserted or pushed again.
3. **Distinct level 0.** A one-hash bitmap of 2^27 bits per searcher, estimated by linear counting. The bitmaps are
   saved at the end, so the distinct count across searchers is computed post hoc from their union.

**Unattended safety.** The memory rule, applied by hand in X1, X3 and X6, is now code: `--mem-stop-mb 1000` stops
the run cleanly when MemAvailable falls below 1,000 MB, and the stop is reported in the journal. It is the same
preregistered rule, applied automatically, so a stop is not a deviation. The budget is 28,800 s (8 h), with 4
searchers, 4 verifiers and seeds 1101+.

**Run:** `python -m soup.t4_setup --dir x7`, then `soup.known build --out /data/x7`, then `podman run -d --name
soup-x7 -v "$PWD/work:/data" -e SOUP_DATA=/data/x7 -e SOUP_VERIFIER=V6 soup python3 -m soup.stream.supervisor --arm
fusion4 --searchers 4 --verifiers 4 --seed0 1101 --budget 28800 --mem-stop-mb 1000 --run x7`.

**Done before this entry, disclosed.**
- `tests/test_x7.py` was added, and the whole suite passes (80 tests).
- A 4-minute engineering smoke run (`work/x7smoke`, seeds 1991–1994, deleted afterwards) checked that nothing breaks.
  Per evaluation it skipped about 7% as known, 0.2% as earlier candidates and 0.05% as seen before. Distinct
  evaluations were about 88% of raw. 15 theories were verified, 5 with a positive score. Nothing else was read.

**Predictions** (descriptive):
- **Q1:** post hoc, `soup.relabel` and `soup.rediscover` find no fragment or subvariety of a named or catalogue
  theory among X7's top 20, and `soup.dedupe` finds no top-20 candidate equivalent to an earlier one.
- **Q2:** the union of the searchers' bitmaps counts at least 80% of raw evaluations as distinct.
- **Q3:** X7's top 20 holds at least 10 distinct varieties, and at least 5 are "disconnected" (X6: 17 and 7).
- **Q4:** the parameter screen fires on less than 24% of verified theories (X6: 24%).

**After the run:** X6's post-run pipeline, with x7 added.
- Fragments, statistics, candidates, profile, `soup.hidden` (plain and `--param`), relabel, rank and rediscover.
- Split per candidate, with the results merged into `check/split_candidates.json`.
- Disconnected marks, dedupe, N1, the funnel, and a REPORT section.

**Caveats:**
- The skips rely on the corpus, which over-approximates implication. A skipped theory may not really be a fragment
  or subvariety: the error goes towards skipping too much.
- The library holds only what our checks and the ledger know, not the literature.
## X6: X5 with the parameter-definition screen, a longer run (written 23 Nov 2026, 06:39 UTC, before X6 starts)

Exploratory and descriptive. The user chose the design on 23 Nov: verifier V6, arm `fusion2` as in X5, not `fusion3`.

**The single change from X5.** Verifier V6 = V5 plus a third stage-a screen. If one operation is a term in the other
plus a constant square (`soup.hidden.hidden_param` on the census models, then E for 10 s), the theory scores 0. Post
hoc, the check catches 18 of X5's 20 top candidates and none of the other 138 candidates (REPORT, "The two filters").

Everything else is as in X5:
- arm `fusion2`;
- 4 searchers and 4 verifiers;
- the memory stop rule (available memory below 1 GB, reported), and nothing heavy alongside.

The seeds are 1001+. The budget is **28,800 s (8 h)**, against X5's 9,000 s. The user asked for more cheap
evaluations (level 0), and a longer run also tests whether the search keeps finding new varieties over time. Counts
are therefore not comparable with X5; shares and per-hour rates are.

Setup: `python -m soup.t4_setup --dir x6`. Run: `podman run -d --name soup-x6 -v "$PWD/work:/data" -e
SOUP_DATA=/data/x6 -e SOUP_VERIFIER=V6 soup python3 -m soup.stream.supervisor --arm fusion2 --searchers 4 --verifiers 4
--seed0 1001 --budget 28800 --run x6`.

**Tests before the start.** The whole suite passes (75 tests, including `tests/test_x6_filters.py`). An engineering
smoke run of V6 (4 min, arm `fusion3`, deleted, REPORT) showed no screen errors.

**Predictions** (descriptive, no p-values):
- Q1: post hoc, `soup.hidden --param` catches none of X6's top 20. A hit would mean the screen leaks, for example
  through census models too few for the term search.
- Q2: X6's top 20 holds at least 10 distinct varieties (`soup.dedupe`). X5 had 5, one of them holding 15 candidates.
- Q3: the attractor of X5, x·(x·x) = y·(x·y), stays among the three most frequent proved emergent laws. `fusion2`
  does not filter it.
- Q4: at least 15 of the top 20 have a classical model. The rigid region is dense in affine structures, and V6 removes
  only the translate disguise.

**After the run**, as for X5, with `x6` added to the sources:
1. fragments, statistics, `notes/x5_predictions.py` extended to x6;
2. candidates (`--sources ...,x5,x6`), profile, hidden, relabel, rank, rediscover;
3. `notes/disconnected.py x6 x5`;
4. split per candidate (`soup.split --laws`, 300 s each; the X5 workaround);
5. `soup.hidden --param` on the candidates (Q1);
6. `soup.dedupe` with `x6`, then `soup.novelty` and `soup.funnel`.

The split scan of all non-fragments comes last and only if time allows.

**Caveats:**
- An 8-hour run grows the corpus more than the earlier runs did, so the cheap score drifts more within the run.
- The census can be small. The parameter screen then works on few models, and Q1 checks for exactly that.

## X5: the fusion arm, restricted to rigid theories (written 22 Nov 2026, 21:37 UTC, before X5 starts; the first commit said 21:40, an estimate)

Exploratory and descriptive. The aim is the user's: steer the search away from X4's attractor and toward fusions
that work but are not clearly connected to known structure.

**Why this restriction, measured before writing this.**
- **X4's attractor.** It was off the diagonal but still about squares: `x · (x · y) = x · x` and its kin. Of X4's 565
  scored theories, 483 (85%) prove a claim with a subterm `s · s` or `s ∘ s`.
- **First design, rejected.** It excluded laws with a square subterm (26,980 of 71,369 laws) and was rejected on two
  measurements, neither from a run:
  1. With those laws as background, McKenzie's positive control loses commutativity. With idempotence, a square law
     such as `x · (y · y) = y · x` is commutativity in disguise.
  2. Without them as background, a sample of 150 X4 theories still gains the same attractor in square-free form.
     The most frequent remaining law is `x · (x · y) = x · (x · z)`.
- **What the attractor really is.** A derived operation of order ≤ 2 that ignores an argument. Call a law
  *argument-ignoring* if it reads `t = t'`, where `t'` is `t` with one variable that occurs once renamed to a fresh
  one. Examples are `x · y = x · z`, `x · (x · y) = x · (x · z)` and `x · (x ∘ y) = x · (x ∘ z)`. There are 53 such
  laws (`soup.offdiag.IGNORE`). On X4's final corpus, 519 of its 565 scored theories (92%) imply one. On samples of 300,
  X4 has 28 rigid theories and X3 has 15. Script: `notes/x5_baseline.py`, output
  `notes/x5_baseline.out`.

**The single change from X4.** Arm `fusion2` is arm `fusion` plus one skip.
- Any theory whose corpus-implied laws contain an argument-ignoring law is skipped and counted in the heartbeats
  (`ign_skipped`).
- The corpus over-approximates implication. So a theory that passes really implies no argument-ignoring law: a
  finite model refutes each one.
- What is left are *rigid* theories, in which every derived operation of order ≤ 2 depends on all its arguments, as
  in quasigroups and rings. Absorption, the lattice region, bands and X4's attractor are all excluded.
- Everything else is as in X4: verifier V5, the off-diagonal score, the lattice skip, the pools, 4 searchers and
  4 verifiers, a budget of 9,000 s. Seeds are 801+.
- The stop rule is as in X3 and X4: available memory below 1 GB, reported. Nothing heavy runs alongside.
- Setup: `python -m soup.t4_setup --dir x5`.
- Run: `podman run -d --name soup-x5 -v "$PWD/work:/data" -e SOUP_DATA=/data/x5 -e SOUP_VERIFIER=V5 soup python3 -m
  soup.stream.supervisor --arm fusion2 --searchers 4 --verifiers 4 --seed0 801 --budget 9000 --run x5`.

**Done before this entry, disclosed.** A 4-minute engineering smoke run (`work/x5smoke`, seeds 901–904, deleted
afterwards) checked that the skip does not starve the search. About 4% of evaluations were skipped, and 12 theories
were verified, 7 with a positive score. Nothing else from it was read.

**Tests before the start** (`tests/test_fusion.py`, the whole suite, 71 tests, passes):
- the masks on named laws;
- absorption, McKenzie's basis and an attractor theory each imply an argument-ignoring law on the corpus;
- the left quasigroup with `∘` its left division implies none.

**Predictions** (descriptive; none is a test with a p-value):
- P1: by construction, no X5 theory implies an argument-ignoring law on X5's final corpus. A violation would be a bug.
- P2: the ten most frequent proved emergent laws of X5 share at most 3 with X4's.
- P3: the share of scored theories with a proved claim containing a square is below X4's 85%.
- P4: the classical constructions (affine, group-derived, rings), which are rigid, model more of the top-20
  non-fragments than in X4. The risk is that X5 mostly finds known quasigroup and ring fragments.

**After the run, as X4** (sources plus `x5`):
1. fragments;
2. top 20 into the candidates;
3. profile, `soup.hidden`, `soup.split`, `soup.relabel`;
4. T5a ranking, dossiers, Lean;
5. `soup.rediscover`;
6. `notes/disconnected.py`;
7. `soup.dedupe`, with `x5` in its corpora;
8. `soup.novelty --readme`;
9. the split scan of X5's non-fragments, last.

**Reported next to X4:**
- theories verified per hour;
- the share with a proved off-diagonal law;
- the ten most frequent proved emergent laws;
- fragment share;
- V4 marks;
- skips;
- FMB refutations;
- identification share of the top 20;
- the disconnected marks;
- N1 entries from X5.

**Caveats:**
- The rigid region is where quasigroups, groups and rings live. Rediscovery there is likely, and the catalogue covers
  it less well than the lattice region, so "unidentified" is weaker still.
- The skip depends on the corpus, which grows during the run.
- An empty or near-empty result is possible and gets reported.

## N1: a novelty ranking of the candidates (post hoc; written 22 Nov 2026, 15:40 UTC, before it is computed)

**Why.** The preregistered T5a ranking sorts candidates by the features that separate named theories from random
ones: a convergent presentation, then a duality. It rewards resemblance to the known, which is right for "is this
the kind of structure algebraists name?" and wrong for the user's aim: a fusion that works but is not clearly
connected to anything known. X4's theories have no duality by design, so T5a puts them low whatever they are. N1 is
a second ranking, used *alongside* T5a, not instead of it. The user asked for it (22 Nov, afternoon).

**Status at the time of writing.** X4's candidate checks (profile, hidden, split, relabel) are running. Two of
their log lines were seen in passing: `d82738a2` not definitional, `94d69dd2` not split. No other X4 candidate
check, no R1 result on X4 and no dedupe result has been read.

**Input.** The candidate pool, `work/check/candidates.json`: the top 20 non-fragments by verified score of each run
(`.`, `t4-prior`, `t4-noprior`, `x1`, `x2`, `x3`, `x4`), plus T1 and T2. It runs after the X4 post-run, R1 on X4, and
`soup.dedupe` on the pool.

**Gate.** A candidate enters N1 only if all of these hold:
1. **It works.** Its verification record has at least one proved emergent law, and its profile shows
   non-degenerate models on at least 2 sizes. Candidates with no verification record (T1, T2) are listed apart.
2. **Nothing identifies it.**
   - Not split (`soup.split` True). `None` is allowed but flagged.
   - Not definitional (`soup.hidden`), and no V4 mark.
   - No relation in `soup.relabel`: none of implies, fragment of, equivalent to.
   - No R1 relation to a catalogue entry: none of fragment, subvariety, equivalent. A relation with "?" is allowed
     but flagged.
3. **One per variety.** From each class of `soup.dedupe` (equivalent under the 8 relabellings), only the member with
   the highest verified score enters.

**Order** among those that pass, lexicographic:
1. A proved emergent law that is **off-diagonal**: not a diagonal law, and in `soup.offdiag.offdiag_gain` on the
   corpus of the candidate's own run. Yes first.
2. **No classical model**, as in the X4 entry: no non-degenerate structured probe on 3 or more elements. Yes first.
3. **Not related** to a known structure by a partial identification in the ledger (`notes/rediscovery.md`). These
   are `10c98c4b` (its core is Δ-bijectivity), `3e068fa6` (its finite models are Δ-bijective pairs) and `31d6d970`
   (its associative case is the rectangular skew lattices). Unrelated first. The list is fixed now; later ledger
   rows do not change N1.
   *Clarification (22 Nov 2026, 18:11 UTC, after `soup.dedupe` and before N1 is computed).* A partial
   identification belongs to the variety, so it applies to every member of the candidate's dedupe class. `soup.dedupe`
   puts `2dc27508`, `69dfbd8e` and `31d6d970` in one class (E both ways under rev∘; equal model counts on 3 and 4
   elements). Its representative, `2dc27508` (highest score), therefore carries `31d6d970`'s flag.
4. **More sizes with non-degenerate models**, from the profile spectrum.
5. **Smaller axioms**: the sum of the orders of the laws.
6. **Verified score**, higher first, as the last tie-break. Scores from different verifiers are not comparable, so
   it only breaks ties.

**Outputs.**
- `work/check/novelty_ranking.json`, and the N1 top 20 with every mark.
- `notes/candidates_table.md` (added at the user's request, 15:43 UTC, before computing), in two tables:
  - **known:** every candidate a check identifies, with what it is and which check said so;
  - **not known as far as our checks and searches go:** the N1 list in order, with its marks as the metric.

  Below them: candidates that fail "works", and those with no verification record.
- A live summary in `README.md`, between `<!-- candidates:start -->` and `<!-- candidates:end -->` (`--readme`;
  added at the user's request before computing): the metric, the counts, and the N1 top 10. It is regenerated each
  time `soup.novelty` runs, which is after every run's checks.
- The gate counts: how many fail each condition.
- The overlap of N1's and T5a's top 10.
- The share of each run in N1's top 10. Expectation, not a test: X4 takes a larger share of N1's top 10 than of
  T5a's.

**Follow-up.**
- New N1 top-10 entries get a dossier, a Lean certificate of the smallest model, and a literature check (a web-only
  agent, key claims rechecked by E). Wording: no candidate is called new without a check by someone who knows the
  field.
- Code: `soup/novelty.py`, committed with this entry, before it is run.

**Caveats.**
- N1 is post hoc and descriptive.
- Its gate depends on our checks and catalogue: "unconnected" means unconnected to them.
- Its first key favours X4 by construction, since X4 selected for off-diagonal laws.

## X4: fusion arm, away from the diagonal and the lattice corner (written 22 Nov 2026, 10:40 UTC, during X3, before X4 starts)

Exploratory and descriptive only: no hypothesis is tested. The user's aim (22 Nov, morning): find theories in the
spirit of the "jazz" example, an original jump of the kind a human makes, and look for strategies that find
legitimate, probably unexplored, valid new theories. Two measurements motivate X4:
- **Coverage.** All runs together verified 4,222 theories against 1.8 × 10²⁶ law sets, and the duality prior keeps
  them in the most-studied corner (`notes/coverage.py`, REPORT "Coverage").
- **A diagonal attractor.** Of the 3,596 theories with a positive verified score in T4, X1, X2 and X3 (10:43 UTC,
  X3 running), 3,478 (97%) prove an emergent law in one variable. The ten most frequent proved emergent laws are all
  about squares (`x·x = x∘x`, `x·(x·x) = x·x`, `x·x = x`, ...), and none of the 3,596 proves emergent associativity.
  So the score rewards what a fusion forces on the diagonal. The lattice absorption pair, our reference case, is
  itself such a case. Script: `notes/diagonal.py`, output `notes/diagonal_pre_x4.out`. A first one-off tally at
  10:40 counted only three laws (`x·x = x`, `x∘x = x`, `x·x = x∘x`): 2,495 of 3,574, 70%. That figure was in this entry's
  first commit, `3faeeb9`.

Setup and arm:
- Setup: `python -m soup.t4_setup --dir x4`, own `SOUP_DATA=/data/x4`, as X2 and X3.
- Search: new arm `fusion` (`soup/stream/searcher.py`, `soup/offdiag.py`). It is arm `noprior` (no duality operator,
  no duality bonus) with three changes:
  1. **Off-diagonal gain.** The cheap score counts only laws that T implies on the corpus and that no single law of
     T implies even together with all the one-variable laws T implies. Weights by order: 1, 0.5, 0.25, 0.125 (the
     old weights gave order-4 laws, such as associativity, weight 0). *Changed after a 3-minute first attempt
     (deviation 6):* "one-variable laws" became "diagonal laws", laws in which each side has at most one variable
     (adding x·x = y·y and its kin).
  2. **The lattice corner is skipped.** Theories that hold in the 2-element lattice are not scored. The count of
     skipped theories goes into the heartbeats.
  3. **Tradition-fusion proposals.** In the 25% slot the prior arm uses for duality closure: one law in · alone and
     one in ∘ alone, each drawn from a pool of restrictive one-operation laws with non-degenerate corpus models at
     three or more sizes, plus one random bridge. These are two "traditions" and a bridge between them. The other
     mutations are unchanged.
- Verifier V5 (`soup/verify.py`) = V4, but stage a draws its claims from the off-diagonal emergent laws. So the
  verified score counts only laws the fusion produces without going through the diagonal. The split and division
  screens of V4 stay.
- 4 searchers and 4 verifiers, seeds 701+, budget 9,000 s. The stop rule is as X3: memory below 1 GB, reported, and
  nothing heavy alongside.
- Tests before the start: `tests/test_fusion.py`.
  - Positive control: McKenzie's lattice basis has commutativity of both operations among its off-diagonal emergent
    laws.
  - Negative control: the absorption pair's emergent `x·x = x` does not count.
  - The 2-element lattice holds the lattice laws and not the Δ-bijective core; the pools are one-operation and
    non-empty.

  The whole suite must pass.

After the run, in this order (as X3, with `x4` added to the sources):
1. the fragment check;
2. the top 20 non-fragments join the candidate list;
3. profile, `soup.hidden`, `soup.split`, `soup.relabel` on the new candidates;
4. the T5a ranking, dossiers and Lean certificates for new top-10 entries;
5. `soup.rediscover` on X4;
6. the split scan of X4's non-fragments, last.

Post hoc, and labelled as such: the off-diagonal gain of X3's verified theories, computed on X3's final corpus, as a
baseline for how often off-diagonal synergy occurs without being selected for.

Reported descriptively, X4 next to X3:
- theories verified per hour;
- the share of verified theories with a proved off-diagonal emergent law;
- the ten most frequent proved emergent laws (does a new attractor appear?);
- fragment share;
- V4 marks;
- theories skipped as lattice-valid;
- FMB refutations;
- the share of the top-20 non-fragments that the post hoc checks identify;
- the top 20 that no check identifies.

Each unidentified one gets a literature check (Latin-square, quasigroup, Yang–Baxter/rack/cycle-set, bisemilattice
and ETP sources). None is called new without that check and a check by someone who knows the field. Our web
searches are weak evidence (REPORT, "Coverage").

**Added 22 Nov 2026, 12:54 UTC, before X4 starts: "disconnected" candidates.** The user confirmed the reading of the
jazz example and added a second one: something that works but is not clearly connected to what came before.
Post hoc, on X4's top-20 non-fragments, and on X3's 19 as a baseline, each candidate gets three marks:
- **works:** non-degenerate models at two or more sizes, and at least one proved emergent law (off-diagonal for X4);
- **unconnected:** none of the checks relates it to anything known. That means no fragment, subvariety or equivalence
  to any of the 13 catalogue entries under the 8 relabellings (R1's method), no V4 mark, not split, not definitional
  (`soup.hidden`), and no relation in `soup.relabel`. A relation left unknown by E's budget counts as unknown, not as
  unconnected;
- **no classical model:** no non-degenerate model on 3 or more elements among the structured probe families (affine
  over ℤ/n, 𝔽₄, Klein, ℤ/n with + and ×, S₃, the min/max and Boolean families, M₃, N₅). Random tables, the complete
  set on 2 elements, and the structures found by the search do not count as classical.

Reported:
- the number of candidates with all three marks, X4 against X3;
- the list of those candidates, each with its literature check.

Script: `notes/disconnected.py`, written during the run, before any X4 result is read. "Unconnected" means
unconnected to our checks and catalogue. It is no claim about the literature, which gets its own check.

Caveats:
- Three changes at once: what X4 finds cannot be attributed to one of them.
- X4 scores differently from X3, so scores are not comparable across the two runs. Shares and counts are.
- The pools and the off-diagonal gain depend on the corpus, which grows during the run.
- An empty result (no theory with a proved off-diagonal emergent law) is a possible outcome, and it gets reported.

## X3: an exploratory run with filters for known disguises (written 22 Nov 2026, 06:45 UTC, before X3 starts)

Exploratory and descriptive only: no hypothesis is tested. The night showed that most top candidates are old
structures in disguise: split theories, and one-operation varieties with their division written as ∘. X3 asks
what the search finds when those two disguises score nothing. The user's framing (22 Nov, morning): measuring
rediscovery should help new findings, not replace the search for them.

- Setup: `python -m soup.t4_setup --dir x3`, with its own `SOUP_DATA=/data/x3`, as X2.
- Search: as X2. Arm `prior`, 4 searchers and 4 verifiers, seeds 601+. No change to the search code.
- Verifier V4 (`soup/verify.py`) = V3 plus two screens in stage a, after the census:
  - **Split screen.** `soup.split.screen` looks for a certificate of non-split on 2–4 elements. Without one,
    `soup.split.prove_split` runs (E, 30 s). A proved split sets `split` in the result and gives verified score 0.
  - **Division screen.** `soup.relabel.check` runs against the left and right quasigroup pairs only, under the 8
    relabellings (E, 10 s per law). If T implies one, ∘ is a one-sided division of · (or the reverse): `division`
    is set and the verified score is 0.

  Neither screen uses the R1 catalogue or anything outside the code (rule 6). Tests: `tests/test_v4.py`.
- Budget: 10,200 s from the start, the same as X2. The first version of this entry (commit `534c1af`) said 10,800
  s. It was changed before the start because X2's available memory reached a minimum of 1,026 MB, just above the
  stop rule, with nothing alongside.
- Stop rule: as X2. The budget runs out, or the VM's available memory drops below 1 GB, which gets reported. Nothing
  else heavy runs next to it.
- After the run, in this order:
  1. the fragment check;
  2. the top 20 non-fragments by score join the candidate list (sources `t4-prior,t4-noprior,.,x1,x2,x3`);
  3. profile, `soup.hidden`, `soup.split` and `soup.relabel` on the new candidates;
  4. the T5a ranking of all candidates, dossiers and Lean certificates for new entries in the top 10;
  5. `soup.rediscover` (R1's method) on X3's verified theories;
  6. a split scan of all X3 non-fragments (`soup.split --fragments 1 --jobs 4`), run last.
- Reported descriptively, X3 next to X2:
  - theories verified per hour;
  - fragment share;
  - split and division marks set by V4;
  - claims refuted by FMB;
  - the share of the top-20 non-fragments that the post hoc checks identify as split, division or a catalogue
    entry;
  - the top 20 and where they land in the ranking.
- Caveats: V4 sets split and division theories to score 0, so X3's archive differs from X2's by construction. The
  comparison is descriptive. The corpus at the start is the main `work/corpus` (as X2).

## R1: rediscovery against a fixed catalogue (post hoc; written 22 Nov 2026, 06:45 UTC, before anything is computed)

Post hoc analysis of existing results. The user's framing (22 Nov, morning): rediscovery has value as a process.
It is measured here against a catalogue fixed in advance.

- Catalogue: `soup/catalogue.py`, `KNOWN`, 13 entries, committed with this section:
  - the 10 named theories of T3 (`soup.calib.NAMED`, unchanged);
  - doppelsemigroups (= mutually interassociative semigroups);
  - weakly associative lattices;
  - Δ-bijective pairs, marked `post_hoc`: it was added because candidate `10c98c4b` contains it.

  Sources are in the file. All entries have laws of order ≤ 4. Quasilattices were dropped: their axioms have
  order 5.
- Data: every verified theory with a law list in `.`, `t4-prior`, `t4-noprior`, `x1` and `x2` (and `x3` after it
  runs).
- For each theory T, entry K and relabelling r (`soup.relabel.relabellings`, 8, including the 3 dualities):
  - **fragment**: every law of T holds in r(K) (r(K) ⇒ T), and T has an emergent law;
  - **subvariety**: T ⇒ every law of r(K);
  - **equivalent**: both.

  Method: a model filter first. The corpus models of r(K) (resp. T) must satisfy the law (`Corpus.implied`). Then
  E proves it: 10 s and 500,000 processed clauses per law. Only proofs count, and an E timeout is "unknown".
  Results are cached per (r(K), law) and per (T, r(K)).
- **Primary outcome:** the number of catalogue entries rediscovered at least once (some T equivalent to, or a
  fragment of, some r(K)). Reported out of 13 and out of the 12 entries that are not `post_hoc`, per data
  directory and overall.
- Secondary outcomes:
  - counts of fragment, subvariety and equivalent per entry and per directory;
  - for the top-20 non-fragments of each run, the share identified by any route (split, division, a catalogue
    relation).
- Positive controls: the lattice fragments of `fragments.json` (as written) must reappear, and `10c98c4b` must be a
  subvariety of the Δ-bijective entry.
- Budget: 6 jobs and a 2 h wall cap, with nothing else heavy alongside. Theories not reached are reported.
- Caveats:
  - Post hoc. The catalogue was written by us after seeing the results, with the help of an LLM working outside
    the search, and it covers only structures with axioms of order ≤ 4.
  - Equivalence is up to the 8 relabellings, not up to arbitrary term equivalence. `soup.hidden` and `soup.split`
    cover two other kinds.

## X2: a second exploratory run, as X1 (written 22 Nov 2026, 04:25 UTC, before X2 starts)

Exploratory and descriptive only: no hypothesis is tested. The user asked that, with time left, a fresh batch of
candidates go through the pipeline again. X1 was cut to 1.5 h (deviation 4).

- Setup: `python -m soup.t4_setup --dir x2`, with its own `SOUP_DATA=/data/x2`. Matrix files are linked; the corpus
  is copied from the main `work/corpus` at setup.
- Search and verifier: exactly as X1. Arm `prior`, 4 searchers and 4 verifiers, verifier V3, seeds 501+. No code
  change to the search or the verifier.
- Budget: 10,200 s from the start (until about 07:20 UTC).
- Stop rule: as X1. The budget runs out, or the VM's available memory drops below 1 GB, which gets reported.
  Nothing else heavy runs next to it: no scans, no profiles, no prover batches. Light reads and docs only.
- After the run, in this order:
  1. the fragment check;
  2. the top 20 non-fragments by score join the candidate list (sources `t4-prior,t4-noprior,.,x1,x2`);
  3. profile, `soup.hidden`, `soup.split` and `soup.relabel` on the new candidates;
  4. the T5a ranking of all candidates, dossiers and Lean certificates for new entries in the top 10;
  5. a split scan of all X2 non-fragments (`soup.split --fragments 1 --jobs 4`), run last.
- Reported descriptively:
  - theories verified;
  - fragment share;
  - claims refuted by FMB;
  - split share among non-fragments;
  - the top 20 non-fragments and where they land in the ranking.
- Caveats: the corpus at the start includes neither X1's models nor X1's corpus. Not compared with X1 or T4 by a
  test.

## X1: exploratory run with verifier V3 (written 21 Nov 2026, night, during T4, before X1 starts)

Exploratory and descriptive only: no hypothesis is tested, and nothing from X1 enters T4's analysis.

- Purpose: more verified theories, from the duality-prior search, for the T5a ranking and the dossiers. The user
  asked to use the rest of the night this way.
- Setup: `python -m soup.t4_setup --dir x1`, i.e. its own `SOUP_DATA=/data/x1`. Matrix files are linked, and the
  corpus is copied from the main `work/corpus` at the time of setup.
- Verifier V3 (`soup/verify.py`): V2 plus Vampire finite model building. Stage b runs it for 60 s on every pending
  claim that E's small run neither proves nor saturates, starting from the smallest size stage a left unsearched,
  or 7. Stage c runs it for 600 s before Mace4. A model counts only after `check_offline.check_finite`.
- Search: arm `prior` (the duality closure and score factor as in T4), 4 searchers and 4 verifiers, seeds 401+.
- Budget: from the start until 07:30 UTC, at most 14,400 s. It starts after the T4 analysis, the T5a profile run
  and the T4 profiles.
- Stop rule: the budget runs out. The run is stopped early only if the VM's free memory drops below 1 GB; that would
  be reported.
- Reported descriptively:
  - verified theories;
  - the share that are fragments (`fragments.py`), without comparison to T4;
  - claims refuted by FMB that stage a missed;
  - the top 20 non-fragments by score.

  The top 20 then go through the profile and the T5a ranking, with the others in its candidate list.
- Caveats:
  - The corpus of X1 starts larger than T4's: it includes tonight's S10 model and the sweep's models.
  - Score and selection are as in T4. V3 refutes more claims than V2, so V3 scores are not comparable with T4
    scores.

## T5a: does an algebraist's profile separate named from random theories? (written 21 Nov 2026, night, before the run)

Why: the synergy score does not prefer named theories (T3, H2), so it cannot pick out theories a universal
algebraist would find interesting. Before candidates are ranked by structural features, those features are tested
on the same calibration set.

Theories: the 130 of T3 (`work/calib_t3.json`): 10 named, 120 random, including the 2 whose T3 verification
crashed. The profile needs only the laws.

Profile: `python -m soup.profile --set t3 --jobs 8` (code at the commit of this section), one child process per
theory, 1,800 s limit. Budgets:
- Mace4 enumerates all models of sizes 2–4 (60 s each) and size 5 (120 s), capped at 3,000 models per size.
- Models are counted up to isomorphism.
- Term functions: up to 60 models of sizes 2–4 for ternary terms (size ≤ 5); up to 120 models of sizes 2–5 for
  binary terms (size ≤ 7); 60 s and 20,000 functions per arity.
- E proves each identity of a candidate term in 30 s and 500,000 processed clauses, for at most 3 candidates per
  kind.

Features, all binary:
- **F1 `malcev_term` (primary):** some term of size ≤ 5 is a majority, Mal'cev, Pixley or minority term, and E
  proves every identity of that kind from the axioms.
- **F2 `finite_free2`:** the binary term functions on the models close under both operations. This is a finite
  free algebra on 2 generators of the variety generated by those models.
- **F3 `convergent`:** an E saturation against x = y passes the `soup.confluence` checks, i.e. a convergent
  presentation of a non-trivial theory.
- **F4 `spectrum3`:** non-degenerate models on at least 3 of the sizes 2–5.

Hypotheses and tests:
- H1: named theories have F1 more often than random ones. One-sided Fisher exact test.
- H2–H4: the same for F2, F3 and F4. One-sided Fisher, Holm-corrected over the three.
- A crashed profile is reported and left out of the test for each feature it lacks.

Use in ranking (fixed now, before any T4 or exploratory-run theory is profiled). Candidates are:
- the 20 best non-fragment theories by V2 score from each T4 arm;
- T1 and T2;
- the 20 best non-fragment theories of the earlier runs;
- the 20 best of the exploratory run, if it runs.

The ranking:
1. Exclude fragments of a named theory (`fragments.py`: valid) and theories that E proves equivalent, both ways,
   to a variety on the standard list (semilattices, bands, rectangular bands, left- and right-zero bands,
   lattices, distributive lattices, quasigroups), on either assignment of the two operations.
2. Rank by the number of features with p < 0.05 after Holm that the theory has. Ties are broken by duality, then
   by the number of sizes with non-degenerate models, then by V2 score.
3. If no feature reaches p < 0.05, nothing is ranked. Candidates are listed with their features, and the profile is
   reported as not calibrated.

Every listed theory is a candidate, not a result (rule 4), until a literature check and the equivalence checks are
done.

Seen before this section: the profile code was debugged on 3 of the 10 named theories, without the random ones:
- lattice: F1 (a majority term of size 4, proved), F2 (4 functions), F4;
- absorption pair: F3, F4;
- left quasigroup: F3.

No random theory and no T4 theory had been profiled.

## T4: duality-prior search against a matched control (written 21 Nov 2026, evening, before the run)

- **Arms.** `prior`: the searcher with the duality-closure mutation and the score factor (1 + number of
  dualities). `noprior`: the same searcher without both (same filters: bridge, non-degenerate model,
  definitional theories rejected; same cap of 6 laws). Code as of the commit that adds this section.
- **Isolation.** Each arm has its own data directory (`python -m soup.t4_setup`): matrix files linked, a copy
  of the corpus store as it stands after the stage-c sweep of 21 Nov 2026 (the common start), and its own
  queue, dedup markers, gate, results, journal and corpus growth. Nothing is shared between the arms while
  they run.
- **Verifier V2** (`SOUP_VERIFIER=V2`, `soup/verify.py`), the score change decided before this run:
  - difficulty of a proved claim = E 3.2.5 `--auto` proof steps / 10 (z3 effort still recorded);
  - a claim E did not prove gets 0.1;
  - stage a verifies one claim per order level (at most 4 pending, 12 tried);
  - every E saturation gets a convergence certificate;
  - stage c starts Mace4 at the smallest size stage a left unsearched.
- **Compute.** Both arms run at the same time on the 11-core VM, each under its own supervisor: 2 searchers
  and 3 verifiers at the start. Rebalancing within an arm is allowed; the total stays 5 processes per arm.
  Budget 14,400 s (4 h) per arm. Seeds: prior 201–, noprior 301– (one per searcher started). z3-solver
  5.4.1.0, E 3.2.5, Mace4 2026-8A.
- **H1 (primary).** Among verified theories with positive score, the share that are fragments of at least
  one of the 10 named theories of T3 (`python -m soup.fragments`; a law is valid by an E or z3 proof, invalid
  by a corpus model of the named theory or a certified saturation) is higher in `prior` than in `noprior`.
  One-sided Fisher exact test, α = 0.05; undecided theories are excluded from the test, and the two bounds
  (undecided counted as fragments, as non-fragments) are reported. Pilot (first session, different verifier,
  control without the definitional filter): 64/97 against 6/59.
- **Secondary (descriptive).** The 10 highest-scoring non-fragment theories per arm, deduplicated across arms
  up to the three dualities and up to equivalence (E proves each theory's laws from the other; compared only
  when the model counts on 2–5 elements agree). None is called new without a literature check and a check
  against the Equational Theories Project data where the theory specialises to one operation.
- **Stop rule.** Each arm runs once for its budget, without extension or rerun. Crashed workers are restarted
  by the supervisor and reported. If a supervisor dies, its arm is reported as it stands; a rerun would be a
  deviation, written before it starts.
- **Known limits, reported with the result.** Only queue-top theories get verified (priority by the cheap
  score): any arm difference inherits this selection. The arms' corpora diverge as each verifies its own
  theories; that is part of each arm. E's proof length is an upper bound on proof length: proof minimisation
  shortens ETP proofs several-fold (Kondylidou, Blanchette, Heule, arXiv:2605.21200: 62 to 20 steps, 151 to
  10), so V2 difficulty ranks proofs only roughly. (Added before the run, after the literature check.)
- **Analysis.** `SOUP_DATA=/data/t4-prior python -m soup.fragments`, the same for `t4-noprior`, then
  `python -m soup.t4_report`.

## T3: calibration, named vs random theories (written 21 Nov 2026, before the run)

- **Theories.** 10 named theories of order ≤ 4 (`soup/calib.py`): lattice, skew lattice, dimonoid,
  absorption pair, left quasigroup, right quasigroup (the first session's six), plus bisemilattice,
  right absorption pair, idempotent left quasigroup, idempotent right quasigroup. (Racks and quandles do not
  fit: left self-distributivity has order 5.)
  Random theories: 30 per size k present among the named ones (k = 2, 3, 5, 6: 120 in all), k distinct
  laws uniform over the 71,368 non-trivial laws, kept if ≥ 1 bridge and a non-degenerate base-corpus model.
  Seed 11.
- **Verification.** `verify` stages a+b with E (z3-solver 5.4.1.0, E 3.2.5), on the shared corpus store.
- **H1 (primary).** Named theories have a duality more often than random ones. Test: one-sided Fisher exact
  test on the 2×2 table (named/random × duality yes/no), α = 0.05. The named theories were chosen by people,
  and several were chosen *because* they are symmetric: H1 is a sanity check of the duality prior, not a
  discovery.
- **H2 (descriptive, no test).** On gain, max difficulty (z3), max E proof steps, model richness and score,
  report each named theory's percentile among random theories of the same size. First-session expectation:
  9th–91st percentiles, i.e. these measures do not separate named from random theories.
- **Stop rule.** All 130 theories verified once; no reruns, no exclusions after the fact. A theory whose
  verification crashes is reported as such.
- **Analysis.** `python -m soup.calib_report work/calib_t3.json`.

## Deviations

1. **T3, k = 6 null (21 Nov 2026, before any calibration result existed).** Uniform rejection sampling
   accepted 0 of 267,682 draws at k = 6 (k = 5: 7 of 308,389; k = 3: 1,650 of 434,019; k = 2: 31,473 of
   549,832; 20 s each). The k = 6 random theories are instead drawn model-first: a non-degenerate base
   structure uniformly at random, then 6 distinct laws it satisfies, at least one a bridge. Same filter,
   different weighting; the 6-law comparisons (lattice, skew lattice, bisemilattice) are reported as against
   this null. k = 2, 3, 5 stay uniform. Fisher's test is reported on all random theories and on the uniform
   ones only.
2. **T3, crashed run resumed (21 Nov 2026, evening, after 69 of 130 results existed).** The run stopped
   at 69 results: the kernel of the Podman VM OOM-killed one worker (python, 5.9 GB resident, 12:56 VM time),
   and the broken process pool ended the whole run. Which theories were in flight is not known; none of them
   has a result. The 69 results were looked at before this deviation was written (duality counts: named 8/10,
   random 0/59); nothing below depends on them.
   - Fix: every theory runs in its own child process. z3 is capped at 1.5 GB (as in the stream verifier);
     E and Vampire are capped at 2 GB. A child that dies, or runs longer than 1 h, is recorded as `crashed`.
     6 theories at a time instead of 10.
   - The 61 theories without a result (1 at k = 2, 5 at k = 3, 25 at k = 5, 30 at k = 6) are verified once
     with the same verifier settings (`verify.V1`). The 69 results are kept and not rerun.
   - A theory that crashes is reported as crashed. It counts for H1, since having a duality is syntactic,
     and is left out of the H2 percentiles.
   - Caveats: the 69 ran without memory caps, which can only turn a run that would have used more memory
     into an unknown; the shared corpus has grown since the start (stream runs), so later theories see more
     structures. Both are reported with the results.

3. **T5a, provers killed by the VM's OOM killer (22 Nov 2026, ~01:50 UTC, after the T5a result was seen).**
   - What happened: the T5a profile ran with 8 jobs, alongside the candidate profile (3 jobs) and `t4_report`,
     which ran 10 E processes at once. The kernel log of the Podman VM shows 10 OOM kills between 01:28 and
     01:41 UTC:
     - `soup-t5a`: 3 profile children, reported as crashed, plus 3 E runs;
     - `t4_report`: 3 E runs;
     - the candidate profile: 1 E run.
   - Why it matters: the profile recorded a killed E run as "not proved" or "did not saturate", which is a
     feature value of 0, not a crash. Which theories were affected cannot be told from the output. The
     analysis as run reported F3 (`convergent`) as calibrated (named 6/10, random 13/117, Holm p = 0.0022) and
     F1, F2, F4 as not calibrated. 3 random theories crashed.
   - Fix (commit after this entry): a prover or Mace4 killed by a signal now gives the value *unknown* for the
     feature it feeds. Per the T5a rule for crashed profiles, an unknown value leaves that theory out of that
     feature's test. `t4_report` takes its pool size from `T4R_JOBS` and reports equivalence checks whose E run
     crashed as unknown.
   - Reruns:
     - all 130 T5a theories, with the fixed code and 4 jobs, nothing else heavy running, into
       `check/profile_t3_rerun.json` (`python -m soup.profile --set t3 --name t3_rerun --jobs 4`), analysed with
       `python -m soup.profile --t5a t3_rerun`;
     - the 62 candidates, from scratch with the fixed code (the partial run is kept as
       `check/profile_candidates_asrun.json`);
     - `t4_report` with `T4R_JOBS=3`. Its primary outcome does not use E, so it cannot change.
   - Reported: both T5a analyses, as run and rerun. Fixed now, before the rerun: the ranking uses only the
     features calibrated in **both** (`soup.dossier rank`).
   - The OOM killer also hit T4 once (searcher s302 of noprior, 00:00 UTC). The supervisor restarted it, as
     preregistered; REPORT lists it with the T4 crashes.
4. **X1, stopped by its memory rule (22 Nov 2026, 03:50 UTC, before any X1 result was analysed).** X1 started at
   02:20:41 UTC with a 14,400 s budget. At 03:50:29 UTC the watcher read 170 MB of available memory in the VM, below
   the preregistered 1 GB, and stopped the run (`podman stop -t 30`; the supervisor's last journal line is
   "stopped by signal" at 03:50:43, the container exit code 137). It ran 1 h 30 min of the planned 4 h.
   - Most likely cause: I started two post hoc split scans (`soup.split --fragments`, 1 job each, each loading the
     corpus) about two minutes earlier, alongside X1's 8 workers. Twenty minutes later the VM had 9.2 GB available
     and the kernel log showed no OOM kill in the last 30 min.
   - Not restarted: the stop rule says stop, and a second start would be a run with a different budget and corpus.
   - Reported: X1 as run (1.5 h), with the descriptive outcomes listed above. The top 20 non-fragments go through
     the profile and ranking as planned.
5. **X3, stopped by its memory rule (22 Nov 2026, 11:08 UTC, before any X3 result was analysed).** X3 started at
   08:33:28 UTC with a 10,200 s budget. At 11:08:32 UTC the watcher read 975 MB of available memory, below the
   preregistered 1 GB, and stopped the run (`podman stop -t 30`; journal "stopped by signal" at 11:08:37; exit code 137).
   It ran 9,304 s, 91% of the budget: 970 theories verified.
   - Likely cause: the run's own memory. The supervisor's PSS total rose from 7,087 MB (10:45) to 8,334 MB (11:07). X2,
     with the same worker count, ended at a minimum of 1,026 MB.
   - Nothing of mine ran in the last 23 minutes. Earlier, during the run, two light read-only containers counted
     result files (`notes/coverage.py` at 10:14, `notes/diagonal.py` at 10:43), each finishing in seconds.
   - The VM also hosts four containers of other projects. Together they use about 120 MB.
   - Not restarted. Reported as run, with the post-run steps as planned.
   - For X4: its budget (9,000 s) is below the point where X3 stopped. The stop rule is unchanged.
6. **X4, stopped after 3 minutes and restarted with a widened definition (22 Nov 2026, 12:58 UTC).** The first attempt
   (`work/x4a`, started 12:55:23) verified 19 theories. 18 had a positive score, and none proved a one-variable emergent
   law, as designed. But 10 of the 18 proved x·x = y·y, and most of the rest proved its kin: x·(x·x) = y·y,
   x·(x·x) = x·(y·y) (`notes/diagonal_x4a.out`). These laws have two variables but speak only about squares. The fusion
   forces the square map to be constant instead of the identity: the same diagonal attractor in another form. The
   entry's stated intent is laws "the fusion produces without going through the diagonal", and these go through it.
   - Change: D, the laws a single law may use, is now every diagonal law T implies: each side has at most one variable
     (`soup.offdiag.DIAG`). The consequences of such laws, such as x·(x·x) = x·(y·y), are then covered through
     implied({t} ∪ D).
   - Tests: `tests/test_fusion.py` gains a mask test and a regression test on x4a's top theory `19b5765e`, where
     x·x = y·y is emergent but no longer counts. The positive and negative controls still pass, and so does the whole
     suite (68).
   - Everything else is as preregistered: arm, seeds 701+, budget 9,000 s from the restart, stop rule, post-run steps.
   - Reported: x4a as a separate 3-minute attempt, with its tally. The first form of the attractor is itself an outcome:
     with one-variable laws excluded, the search found the next diagonal loophole within three minutes.
7. **X4 post-run: `soup.split` on the candidates stopped after 17 of 20 (22 Nov 2026, 17:28 UTC).** The step ran from
   about 15:37. For a candidate with no finite certificate, `prove_split` gives E up to 200 attempts of 30 s, so the
   last 3 could have taken about five more hours.
   - Results by then: 14 not split (finite certificate), 3 undecided.
   - The 3 left (`f1f50575`, `33eca86a`, `d82738a2`) passed V4's split screen during the run, like every X4 theory
     with a positive score. N1 flags them "split not run", as its gate already allows.
   - `soup.relabel` then ran on its own. Every other post-run step is unchanged.
8. **X5 post-run: the split check of the candidates was rerun per candidate (23 Nov 2026, about 01:00 UTC).**
   - `soup.split --set candidates` goes through the candidates in file order. Capped at 1,800 s, it stalled on one
     of X4's three unchecked candidates (deviation 7) and checked none of X5's.
   - It was rerun per candidate (`soup.split --laws`, 300 s each, 4 in parallel). Result: 0 split, 1 not split,
     19 undecided (REPORT, X5).
9. **X6 stopped by its memory rule (23 Nov 2026, 12:25 UTC, before any X6 result was analysed beyond the progress
   counts in the journal).**
   - X6 started at 06:40:02 UTC with a budget of 28,800 s.
   - At 12:25 UTC the VM had 702 MB available, below the 1 GB rule. The X6 container held 11.06 GB: the workers'
     PSS was 7.3 GB, and prover child processes are not counted in it.
   - `podman stop -t 120` ended it cleanly at 12:26:33 UTC, after 20,790 s (72% of the budget). The kernel log shows
     no OOM kill.
   - Results by then: 1,460 verified, 645 with a positive score, 4,004,695 cheap evaluations, and 8,055 structures
     added to the corpus.
   - Every post-run step is unchanged. Counts are for the 5.8 hours that ran, and per-hour rates are computed on
     those hours.

10. **X8 stopped by its memory rule after 70 minutes, because of an image rebuild next to it (24 Nov 2026, 10:19 UTC;
    written 10:26 UTC).**
    - X8 started at 09:09:52 UTC with a budget of 32,400 s.
    - At 10:13 UTC a `podman build` was started next to the run, for a reporting-only change (a Chao1 caveat in
      `soup.taxonomy`). This breaks the rule "nothing extra next to a stream run".
    - About an hour earlier, 78 old soup images had been removed to free disk space. `podman rmi` also removed their
      untagged parent images, which were the build cache, so the build compiled the provers from source.
    - At 10:19:29 UTC the VM had 754 MB available, below the 1,000 MB rule. The supervisor stopped the workers, and the
      run ended at 10:19:37 UTC after 4,183 s (13% of the budget). Exit code 0, no OOM kill.
    - Results by then: 49 verified, 33 with a positive score, 8,453,911 cheap evaluations. The queue (1,500 pending,
      3 in stage c) is kept for the next run.
    - **Decision (user, 10:29 UTC):** continue as run `x8b` in the same data directory (`SOUP_DATA=/data/x8`).
      - Settings unchanged, except seeds 1209 onward (X8 used 1201–1208) and the remaining budget, 28,217 s.
      - Nothing else runs beside it, not even a build.
      - R1–R4 are judged over X8 and x8b together, and the report gives each part's counts separately.

11. **X9 stopped by its memory rule after 2 hours, once X8's copied queue was empty (25 Nov 2026, 00:29 UTC; written
    00:38 UTC, after S1–S4 were computed but before anything else).**
    - X9 started at 22:28:27 UTC with a budget of 28,800 s.
    - The pending lane was empty at 00:28:24 UTC. 1,255 of the 1,256 copied theories had a result, and the last one
      was still claimed.
    - With nothing pending, the verifiers took stage-c tasks: six of the seven were in stage c at 00:29:29 UTC. Until
      then two or three had been in stage c at a time, and memory had held.
    - At 00:29:45 UTC the VM had 362 MB available, below the 1,000 MB rule. The supervisor stopped the workers, and the
      run ended at 00:29:58 UTC after 7,291 s (25% of the budget). Exit code 0, and the kernel log shows no OOM kill
      during the run.
    - **The design was wrong on one point.** It said searchers would start once the queue ran low, and none did. The
      rebalancer starts a searcher only in place of an idle verifier, and a verifier with nothing pending takes
      stage-c work instead of going idle. So X9 made no cheap evaluations.
    - Results by then: 1,262 verified, 808 with a positive score, 9,118 structures added to the corpus. The queue
      left (1 pending, 156 in stage c) is kept for the next run.
    - S1–S4 are judged on the 2 hours that ran, and per-hour rates use those hours. Nothing else changes.
    - The VM also holds the user's other containers, idle, with about 0.7 GB between them. They have been running since
      before X9 and its smoke runs.

12. **X10's first block, x10a, stopped by its memory rule after 39 minutes (25 Nov 2026, 14:30 UTC; written 14:33 UTC,
    before anything was computed from the block beyond its journal and stats lines).**
    - x10a started at 13:52:25 UTC with a budget of 7,200 s (`--drain-c 3600`, seeds 1401–1406), as in the second
      amendment.
    - At 14:30:57 UTC the VM had 642 MB available, below the 1,000 MB rule. The supervisor stopped the workers, and the
      block ended at 14:31:16 UTC after 2,313 s. Exit code 0, and the kernel log shows no OOM kill.
    - **What happened:** between the ticks at 2,289 s and 2,311 s two verifiers grew at once, v0 (stage b) from 574 to
      1,739 MB and v2 (stage c) from 852 to 1,552 MB, so the workers' total PSS went from 5,872 to 7,678 MB. Each
      prover is capped at 2,000 MB, but nothing stops two from peaking together.
    - **What was different from the smokes:** a five-container web stack of the user's, which was not running during
      the smoke runs, started beside the block (its database at 13:45:38 UTC, the other four at 13:53:58 UTC). At the
      stop it held about 1.1 GB, and its frontend used about a quarter of a core. Without it the low point would have
      been near 1.7 GB, above the rule; that is an estimate, not a measurement.
    - Results by then: 24 verified (6 with a positive score), none through stage c, 2 stage-c tasks cut by the stop,
      1,684,503 cheap evaluations, 38 structures added to the corpus. The queue (1,500 pending, 157 stage c) is kept.
    - The searchers made about 0.45M evaluations per searcher-hour (from the stats ticks), against 0.60M in the second
      smoke. That stack's CPU may explain part of that; it was not measured.
    - As the second amendment says, the 2,313 s count toward the 28,800 s (26,487 s left), U1 fails, and the next block
      may still run.
    - **Two details from the stats** (read at 16:20 UTC): the last tick, at 14:30:56 UTC, logged 599 MB available, and
      the rule read 642 MB a second later. Between the ticks at 2,270 s and 2,289 s available memory fell by 1,535 MB
      while the workers' PSS rose by 384 MB. The rest was outside the workers, most likely a stage-c prover's child
      process, which a worker's PSS does not count.
    - **The user's decision** (recorded at 16:23 UTC): the stack keeps running during the blocks. From x10b on, blocks
      run with 4 searchers instead of 6 (third amendment, written before x10b starts).
13. **X12, two of fusion5's verifiers stuck in stage a for most of block x12a (found 27 Nov 2026, about 04:45 UTC,
    after the post-run checks and the judging of Y1–Y8; written 05:05 UTC).**
    - Block x12a ran to budget in both arms, 26 Nov 19:28:05 to 27 Nov 03:28 UTC, with no memory stop. But fusion5 wrote
      no result after 22:16 UTC: its results per hour were 328, 87 and 145, then 0 for five hours.
    - **What happened:** fusion5's v2 wrote its last result at about 20:10 UTC and v8 at about 22:16 UTC. Both then
      stayed in stage a on one claimed theory each, 7.3 and 5.2 h, until the stop put both tasks back. Every stats tick
      shows them in "stage a", and the queue showed 2 claimed throughout. In finished tasks fusion5 used 3.08 of its
      16.0 verifier-hours, fusion6 10.84 of 16.03 (`notes/x12_table.py`, `notes/x12_table.out`).
    - **Cause** (`notes/x12_hang.py`, `notes/x12_hang_28801.out`, `notes/x12_hang_71025.out`, `notes/x12_cap_check.out`):
      - The two theories (keys `52ef5b80`, `7046daba`, both from searcher s1801) have five laws each, and both include
        x·x = y·y.
      - Stage a rerun on a copy of x12-f5's corpus stayed in one z3 call for 20 minutes in both: stack dumps at 5, 10
        and 15 minutes, killed at 1,200 s. The call is the redundancy proof of x·x = y·y from the other four laws
        (`verify.stage_a` → `core.prove`), which only its rlimit of 10M bounded.
      - With a 60 s cap that proof reached an rlimit count of 0.99M and 1.53M. The other eight redundancy proofs of the
        two theories reached 10M in 4 to 40 s. z3's counter grows too slowly there for the rlimit to bind within hours.
    - **fusion6, the same cause by another route** (found 05:15 UTC): four of its verifiers died with z3's
      `out_of_memory_error` (exit −6) at 23:55, 01:06, 02:15 and 03:24 UTC, each with one task claimed, which the
      supervisor put back. The restarted verifier took the head of the lane again, `ff914371`, still first in
      `work/x12-f6/queue/pending` at the end: about 4.6 verifier-hours. Rerun under V8 (`notes/x12_hang_f6_4888.out`),
      its stage a took 567 s, nearly all in redundancy proofs stopped by the 120 s cap, and the task finished in 980 s;
      under V7 they ran until z3's
      1,500 MB memory cap aborted the process. That attribution rests on the stack, the timing and the lane order; it
      was not rerun under V7.
    - **Why nothing noticed it:** the supervisor watches memory and heartbeats, and a verifier inside z3 still sends
      heartbeats. The host watcher read the journal and `stats.jsonl`, which kept being written. The crashes were
      journaled, but nobody read the journal between the 72-minute check and the end of the block.
    - **Effect on the predictions:** they were judged as preregistered, and all their inputs are complete. But the arms
      got unequal verifier time: fusion5 verified 560 theories, nearly all in its first 3 hours, fusion6 734.
      - Y1 compares at equal sample size, Y2 and Y3 are shares, Y7 and Y8 are not about sample size.
      - Y4 (the top 20 of fewer verified theories) and Y5 (a count) depend on how far down its queue an arm got. Post
        hoc, by exact rarefaction at fusion5's 266 structured theories, fusion6 has 51.8 expected new families against
        4.0, so Y5's verdict does not depend on it. Y4's may.
      - Each arm verified its queue in priority order, so fusion5's 560 are the head of its queue, and fusion6's 734
        reach further down its own.
    - **Fix** (after the run, before any further run): verifier V8 is V7 plus a wall-time cap on every z3 proof, 120 s
      in stages a and b and 1,800 s in stage c (`core.prove(..., secs)`, z3's own timeout; `tests/test_z3cap.py`). A
      capped proof ends "unknown", as one that reaches its rlimit does. V7 is unchanged.
    - X12's budget, 28,800 s per arm, was spent in this one block, so X12 is complete. Nothing is rerun.
14. **R2 (review item B1) stopped and restarted with a faster model filter (28 Nov 2026, 10:10 UTC; written 10:17 UTC).**
    - The first run started 08:34:36 UTC. G and AG finished (596 s and 20 s), and the rings entry R was still running
      after 1.4 h. The filter called `law_vector` (all 71,369 laws, about 10 ms) once per ordered pair of term classes
      and per model, so its cost grows with the square of the class count. R, BA and HA have 1,382 to 2,788 terms
      against G's 268, so HA, where the positive control R2a lives, would not have been reached within the 8 h.
    - **Stopped** at 10:10:52 UTC after 5,776 s. G and AG were saved, and R's partial work was lost. R2b's outcome was
      already in the log at the stop: 18 random theories are fragments of G or AG. The stop was decided on the
      filter's cost, not on that outcome.
    - **Change:** `interp.filter_pairs` tests, for each first term, all second terms at once, law by law, and evaluates
      only the target laws (`holds_batch`; `tests/test_interp.py` checks it against `law_vector` on random and
      structured tables). The test, the entries, the order and the proof stage are unchanged. Rerun on AG and G into
      `check/interp_r2_check.json`: the same classes and the same 28 and 48 survivors with the same results; G's filter
      took 2 s.
    - **Restarted** at 10:14:40 UTC on the remaining entries, in the listed order, with `--wall 23024` (8 h minus the
      5,776 s used), image 76099b5ebaaf.
15. **R2 stopped a second time, and restarted with lazy term classes and a refutation step (28 Nov 2026, 12:19 UTC;
    written 12:24 UTC).**
    - After deviation 14 the rings entry R spent 4,473 s on term classes. Rings with 1 on at most 6 elements are all
      commutative, and Mace4 gave 9 of them, so many distinct terms agree on every model. E then fails on each such
      pair and uses its full 10 s. The filter took 69 s and kept 262 pairs. From 11:30 UTC the proof stage was running
      E 60 s and then Vampire 60 s on each of them, which projects to about 4.4 h, so HA was again out of reach.
    - **Stopped** at 12:19:15 UTC, after 7,475 s of the second run. R's results were not saved. Nothing of R's outcome
      was read beyond the two counts above.
    - **Changes,** neither of which changes a "fragment" verdict:
      - The filter runs on the model groups. The E step of the term classes runs only inside groups that occur in a
        surviving pair. Terms of one group have the same tables, so the survivors are the same as before. A group with
        several members also gets its diagonal pair, which covers two classes in one group.
      - Before the proof stage, each survivor is evaluated on K's Mace4 models of 7 and 8 elements (200 per size,
        120 s per size). A survivor that fails there ends "not (size n)" and is not sent to the provers. E and Vampire
        are sound, so no such survivor could have been proved, and only the "unknown" count changes. Proofs that would
        start after the wall time end "not run (wall)".
    - **Check:** AG and G rerun into `check/interp_r2_check.json` gave the same 28 and 48 survivors with the same
      results, in 6 s and 9 s.
    - **Restarted** at 12:22:42 UTC on the remaining entries in the listed order, with `--wall 15549`, image
      d258211c735a. The class counts in the output now cover only the refined groups (`groups`, `groups_refined`,
      `classes_in_refined_groups`).
16. **R2's HA entry run beside the ordered run (28 Nov 2026, 12:42:57 UTC; written 12:43 UTC).**
    - At 12:42 UTC the ordered run was in R's proof stage: 268 survivors, 150 refuted on 7-8 elements, 118 left for
      E and Vampire, up to about 2 h. CR, BR, DL and BA come before HA, so HA, which holds the positive control R2a,
      would probably not start before the deadline (16:41:51 UTC).
    - HA runs in its own container from 12:42:57 UTC with `--entries HA --jobs 1 --wall 14300 --out interp_r2_ha.json`,
      the same image and code, so it ends by the same deadline. The ordered run skips nothing, and if it reaches HA it
      runs it again; both results are reported. Only the order changes, not the test.
    - **Amended at 13:29:26 UTC.** HA kept 985 survivors after its filter, and its 400 models on 7-8 elements refuted
      none of them. With one job and up to 120 s per unprovable pair, the proof stage would not have ended before the
      deadline. The hypotheses count theories, not pairs, so the proof stage now works in rounds: one pair per theory
      per round, smallest terms first. A theory stops at its first proved pair, and its other pairs end "not run
      (theory already a fragment)". Rerun on AG and G: the same 16 and 4 fragment theories. HA was restarted with
      `--jobs 2 --wall 11546` (same deadline, image d4dca7651f90); its first 46 minutes were discarded. The ordered run
      keeps the earlier image and proves every pair.
    - **Amended at 14:28:37 UTC.** HA's parallel run finished at 14:28 UTC. The ordered run had finished CR, BR, DL and
      BA and was starting HA a second time with the earlier proof order, which would have used the rest of the budget
      and left Hp, Rk, Qd and Qg unrun. It was stopped before any HA result, and Hp, Rk, Qd and Qg were started in its
      place (`--entries Hp,Rk,Qd,Qg --jobs 2 --wall 7994`, image d4dca7651f90, same deadline). HA is reported from
      the parallel run alone.
