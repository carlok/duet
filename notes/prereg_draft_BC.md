# Draft preregistrations for review items B and C (28 Nov 2026; nothing computed)

**Status, 28 Nov 08:15 UTC.** The user approved B1, B3, C3 and C4. They are in PREREGISTRATION.md ("Review items B1,
B3, C3, C4"), with two corrections listed there. B2, B4, B5, B6, C1 and C2 below are backlog: drafts, not approved.

These answer parts B and C of the external review of 279157e (REPORT, "N2"). Each entry moves into PREREGISTRATION.md
and is committed only after the user approves it, and only then is anything computed. All of it is post hoc and stays
out of the search (rule 6). Nothing runs beside a stream run.

**Two changes from the review's wording:**
- **N3, not N2.** N2 was preregistered (9f04af5) before these drafts, with N1's six keys. A mark from B2–B5 that
  separates in calibration becomes a key of a new ranking, N3, preregistered on its own, so that N2 stays fixed.
- **Two steps would send data to outside services:**
  - B6's ETP implication-graph class needs the ETP's implication data, a download.
  - B6's OEIS lookups are web queries.

  Both wait for the user's OK. Everything else runs offline in the image.

**Claims checked before writing:**
- **B1:** `relabel.py:63`, `known.py:51`, `equiv.py:58` and `rediscover.py:47` each skip an entry with a law outside
  the table. Distributivity and self-distributivity have order 5, and interchange has order 6.
- **B3:** under the strict reading (an operation never occurs anywhere below itself), 10 of the 11 level-8 theories and
  28 of the 78 level-7 theories qualify. Under the loose reading (never directly inside itself) it is 10 and 35. The 7
  level-7 theories with non-degenerate models on 4 sizes are N1 ranks 1–7 exactly.
- **B4:** N1's "classical model" is the base probes whose names are not random tables, on 3 or more elements
  (`novelty.py:128–129`).
- **C1:** the candidates are 318 of the 6,651 non-fragments.
- **C3:** both identified theories (`a9295908`, Heyting; `71fd2cc6`, g-dimonoids) were outside the catalogue when they
  were identified.

---

## R2: a library of structures beyond the law table, and `soup.interp` (review B1)

**Question.** How many candidates are fragments of a classical structure under a term interpretation that our order-4
law table cannot express?

**Entries, fixed here.** Each entry is a TPTP axiom set in its own signature, with constants and unary operations
allowed.
- G: groups. AG: abelian groups.
- R: rings with 1. CR: commutative rings. BR: Boolean rings.
- DL: distributive lattices. BA: Boolean algebras. HA: Heyting algebras. Hp: hoops (·, →, 1).
- Rk: racks. Qd: quandles (▷ and its inverse).
- Qg: quasigroups (·, \, /).

Axioms come from the TPTP library (ALG, GRP, LAT, RNG) where it has them, otherwise from Jipsen's Mathematical
Structures pages, each source cited in `soup/interp.py`.

**Term pairs.** The binary terms in x, y of each entry's signature with at most 3 operation symbols (constants and
unary operations count), that depend on both x and y, up to equality in the entry (E, 10 s). (·, ∘) ranges over
ordered pairs of distinct such terms. For BA, the 10 essentially binary Boolean functions give the 90 ordered pairs.

**Test.** "T is a fragment of (K; t1, t2)", checked in two stages.
1. **Model filter:** Mace4 models of K on sizes 2–6, up to 200 per size and 120 s per size. t1 and t2 are evaluated
   to tables, and every law of T must hold in every model (`law_vector`).
2. **Proof:** E proves each law of T, translated through t1 and t2, from K's axioms. 60 s per law; Vampire 60 s for
   what E leaves.

The result is "fragment" (all laws proved), "not" (a model of K fails a law) or "unknown".

**Hypotheses.**
- **R2a, positive control:** with no hint, `a9295908` comes out as a fragment of HA with · = ∧ and
  x∘y = (y→x)→y. (y→x)→y has 2 symbols.
- **R2b, calibration:** none of T3's 120 random theories is a fragment of an R2 entry. A false-positive check, since
  every reported fragment is proved.
- **R2c, descriptive:** the number of N2's level-6 and level-7 theories that are fragments, by entry.

**Budget:** at most 4 jobs and 8 h of wall time. Entries are run in the order listed.

## Determined (review B2)

**Mark.** ∘ is *determined by ·* in T when T(·, ∘) ∪ T(·, ∘′) proves x∘y = x∘′y, which is Padoa's test, and likewise
for · by ∘. By Beth's theorem a proof means ∘ is first-order definable from ·. It is a mark, not a screen: lattices
and quasigroup pairs have it.

**Procedure.**
1. **Filter on exhaustive models, n ≤ 3** (`soup.profile.all_models`): if two models share the · table and differ in
   ∘, ∘ is not determined. That is a finite certificate.
2. **Otherwise E, 120 s, then Vampire, 120 s,** on the doubled theory in TPTP: three function symbols, so the
   wrappers get TPTP text.

The outcome is determined, not determined (with the certificate), or unknown.

**Calibration (as T5a).** The catalogue's entries that are order-4 law sets (the 10 named theories plus
doppelsemigroups and weakly associative lattices) against T3's 120 random theories.
- **Criterion:** Fisher's exact test on "∘ or · determined", two-sided. It separates if p < 0.01.
- **If it separates:** a candidate key for N3 and an F1 subtype, each preregistered separately.
- **If it does not:** it is reported on the candidates as descriptive only.

## Free (review B3)

**Measures,** in both directions, on the exhaustive models at n = 3 and on 200 sampled ·-reducts at n = 4 (Mace4,
seeded):
- **Choice entropy:** for each reduct F, k(F) = the number of ∘ with (F, ∘) ⊨ T. H = mean of log k(F) / (n² log n).
- **Rectangularity:** for each F, the product of the per-cell value sets of its models. 200 tables are drawn from it
  (seeded) and the share of models among them (`split.holds`) is ρ. 1 means the model set is a product over cells.
- **Certificate:** T proves s·(x∘y) = s·t(x,y), or (x∘y)·s = t(x,y)·s, for some ·-term t with at most 2 symbols.
  Model filter, then E 30 s per t. This is an axiom of `bc43fd42`, `d0e963d9` and `d14ced44`, and a theorem of
  `71fd2cc6`.

**Hypotheses.**
- **F1:** the catalogue entries have a lower H and ρ than T3's random theories. Mann–Whitney, two-sided, p < 0.01 per
  measure.
- **F2:** on N2's level 7, H and ρ are higher than on T3's random theories. This is the review's claim that N1's
  sizes key prefers loose theories.
- **F3:** among N2's level-7 theories, those with non-degenerate models on 4 sizes have higher H than the rest.

A measure that passes F1 becomes a candidate N3 key, preregistered separately.

**Budget:** n = 3 is exhaustive; n = 4 is 200 reducts per theory and direction, 600 s per theory, 4 jobs.

## Classical models beyond the probes (review B4)

**Search.** `soup.linear --models T`: models of T with no goal, both operations essentially binary and · ≠ ∘.
- **Linear and affine** over its rings (ℤ/n and GF(q), q ≤ 64; affine for q ≤ 16).
- **Matrix models, new:** x·y = Ax + By + c and x∘y = A′x + B′y + c′ on (ℤ/2)², (ℤ/2)³ and (ℤ/3)², with all
  matrices.
  - A law's truth is decided from its coefficient words in the matrices: for each variable, the coefficients of the two
    sides must agree in the matrix ring, and so must the constants.
  - The · laws are enumerated first, then ∘. 600 s per theory.
  - Every model found is re-checked on its tables.
- **R2's interpreted tables** (B1) also count as classical models.

**Reported:**
- how many of N1's 78 and of N2's level 7 keep "no classical model";
- per family: linear, affine, matrix, R2.

Matrix models in stage b would be a verifier change, and a later preregistration.

**Calibration:** none. This is a broader search for the same mark. The share of T3's random theories that have such
a model is reported beside it.

## Poset and cores (review B5)

**Implication** among N2's ranked theories, under the 8 relabellings.
- First a model filter on the union corpus: the bit-vector test of `known.Library`.
- Then E, 60 s per law.
- The output is the preorder, its Hasse diagram over the dedupe classes, and `notes/poset.md`.

**Minimal axiom sets.** For each proved emergent law, every subset of T (at most 63) is tried: model filter first,
then E 30 s. The minimal proving subsets are listed. Each maximal non-proving subset gets a countermodel from the
corpus or from Mace4 on sizes up to 6, or is marked unknown.

**Clusters.** A and B are linked if one implies a relabelling of the other, or if they share an axiom under some
relabelling and a proved emergent law. Clusters are the connected components. A cluster's core is its shared axioms;
E then checks, 60 s per law, which of the members' emergent laws the core alone proves.

**Positive controls:** three clusters found by hand must appear:
- {`1f430506`, `1238c063`}, with core A;
- {`bc43fd42`, `d0e963d9`, `d14ced44`};
- {`3818b88f`, `de0c0cf3`}.

**Reported:** level 7 in theories and in clusters.

**Budget:** 6 h, 4 jobs.

## The memo's first steps by machine (review B6)

**One command per theory,** `soup.firstlook KEY`:
1. **One-operation laws.** The laws of order ≤ 4 each reduct implies: model filter on the union corpus and on Mace4
   models with n ≤ 4, then E 15 s each. Each is given its ETP number.
   - The ETP implication-graph class waits for the user's OK, since it needs the ETP's implication data, a download.
2. **Seven extensions.** T plus each of: x·y = x∘y; associativity of ·; associativity of ∘; commutativity of ·;
   commutativity of ∘; idempotence of ·; idempotence of ∘. Each goes through the whole identification pipeline:
   fragments, split, hidden and `--param`, relabel, R1, and R2 once it exists.
3. **Counts.** Labelled and isomorphism-class counts for n ≤ 5, of T and of both reducts. Mace4 with a cap; n = 5 is
   reported as incomplete where the cap stops it.
   - The OEIS lookup of the count sequences waits for the user's OK, since it is a web query.

This replaces N1's fixed list of three "related" entries for theories studied after approval. N1 and N2 keep theirs.

**Calibration:** the 13 theories already studied by hand. The command must reproduce each memo's reduct laws and
extension results, and any difference is reported.

**Budget:** 1 h per theory; level 7 first, in N2 order.

## N3: the gate over all non-fragments (review C1)

**Pool:** all 6,651 verified non-fragments (funnel level 3), not the top 20 per run.

**Gate:** N2's corrections, applied in their cheap forms first.
- the param screen, from the results' `screen` field and `soup.hidden --param`;
- R1, which already covers every verified theory;
- relabel, with its model filter;
- split, with its finite certificate on sizes 2–4.

The expensive forms (split proofs, decide, reprove) run only for theories that carry every mark.

**Dedupe:** bucket by the corpus-implied law vector on the union corpus, canonical under the 8 relabellings. E (20 s
per law) runs only inside a bucket.

**Reported:**
- how many theories with every mark are outside the top 20s;
- N3's levels 5–7 beside N1's and N2's.

**Budget:** 24 h of wall time at 4 jobs, cheap stages first. If the budget runs out, the theories not reached are
reported as unchecked.

## Structural laws of order 5 and 6 as claim targets (review C2)

**List, fixed here:** every relabelling (the 8) and side swap of:
- left and right distributivity of · over ∘ and of ∘ over ·;
- left and right self-distributivity of each operation;
- mediality and paramediality of each operation;
- interchange (x·y)∘(z·w) = (x∘z)·(y∘w);
- left and right Bol, and the three Moufang identities, for each operation.

Deduplicated, this is a few hundred laws, counted when built. They are evaluated on corpus tables by a tree evaluator
(`split._ev` generalised), and used as claim targets only.

**Count:** how often each is a proved emergent law over the 7,934 theories with an emergent law. Three steps:
1. a model filter: it holds in every union-corpus model of T;
2. emergence: no single law of T implies it on the corpus;
3. E, 10 s.

**Order and budget:** the 318 candidates first, then the other theories in a seeded random order. 12 h at 4 jobs; the
part not reached is reported as unsampled.

An arm that takes these laws as axioms would be a later preregistration.

## A false-novelty rate (review C3)

**Test set.**
- Known two-operation structures in neither catalogue (R1, R2), fixed here from Jipsen's pages and the TPTP library:
  - MV-algebras (⊕, ⊙);
  - Brouwerian semilattices (∧, →);
  - implication algebras;
  - BCK-algebras with ∧;
  - residuated lattices (∧, \);
  - near-rings (+, ·);
  - bisemilattices;
  - Kleene lattices (∧, ∨).
- **Fragments:** for each structure, 10 fragments: seeded random sets of 2–4 order-≤4 laws true in it, at least one
  of them a bridge, under a random relabelling. A law counts as true when a model filter passes and E proves it.

**Procedure.** Each fragment goes through levels 1–7 as if a run had found it: verifier V8 stages a and b, then the
post-run pipeline and N2's gate and marks.

**Reported:** the share that reaches level 7, the false-novelty rate, next to the 78, with a binomial 95% interval.

**Budget:** 80 theories; the verifier at 2 jobs; 12 h.

## A first statement across families (review C4)

**Single-cell hypothesis (SC), with ties.** Every law of T is one of two kinds, and ∘ occurs only in subterms u∘v
with u and v free of ∘:
- **constraint:** all its ∘-subterms are the same pair (u, v), or the swapped pair (v, u) when T proves ∘ commutative;
- **tie:** it is exactly u∘v = u′∘v′.

**Lemma.** Under SC, for every · on a finite set, the set of ∘ with (·, ∘) ⊨ T is a product over the classes of the
tie relation on cells.
- The tie relation is the equivalence generated by the instances of the tie laws, which depend on ·.
- Each class takes one value, from the intersection of its cells' allowed sets.
- Without tie laws the product is over single cells.
- **Lean:** proved beside `Delta.lean` for the law grammar of order ≤ 4, without `decide`, with the axiom audit.
- **Empirical side:** ρ = 1 (B3) for every SC theory without ties. With ties, ρ is measured over the tie classes.

**Classification:** each of the 170 (N1's level 6) and N2's level 6 gets one of SC without ties, SC with ties, or
neither, for ∘ given · and for · given ∘.

**Hypothesis:** the five theories studied by hand where ∘ is a constrained choice are SC.
- `1f430506` and `1238c063` are SC without ties.
- `3818b88f` (x∘(x·y) = x∘y), `de0c0cf3` ((x·y)∘y = x∘y) and `71fd2cc6` (x∘(x·y) = y∘x) are SC with ties.

Checked against their axioms while drafting. A first draft without ties had them wrong. Any theory that fails
narrows the lemma's reach and is reported.

**Budget:** classification is syntactic, minutes. Lean is exploratory, with no deadline.
