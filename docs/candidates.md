# Candidates studied closely

[← README](../README.md)

Each has a memo in [`notes/`](../notes). Identifications go into the ledger
[`notes/rediscovery.md`](../notes/rediscovery.md). None of these theories is claimed new.

## X6's top entries (N1 ranks 1, 3, 4, 5), and X7's `de0c0cf3` (rank 2)

- **`3818b88f`: a triple system with a selector.** It is equivalent to a totally symmetric quasigroup `·`
  (commutative, `x · (x · y) = y`) with an idempotent `∘` such that `x ∘ (x · y) = x ∘ y` and `(x · x) ∘ x = x` (E,
  both ways). So `x ∘ y` depends only on `x` and the block `{x, y, x · y}`. No source pairs a triple system with
  such an operation. But ∘ is very free: on 4 elements, any choice of one value per (point, block) works
  (`notes/3818b88f_models.py`), so this may be a known kind of structure, a choice function on a triple system.
- **A family of three (`bc43fd42`, `d0e963d9`, `d14ced44`).** All three strengthen a common core in different ways:
  every square is a right identity for `·`, and left multiplication cannot tell `y · z` from `z ∘ y`. With `·` =
  `∘` each becomes the left-zero band.

None is identified. Memo: [`notes/x6_top4.md`](../notes/x6_top4.md).

## `de0c0cf3` (X7, N1 rank 2): `3818b88f` with one law fewer

T = {x·(x·y) = y, (x·y)∘y = x∘y, (((x·x)∘x)·y)·y = x}.
- **Plain reading** (E both ways): `·` is a totally symmetric quasigroup, and `∘` is idempotent and, for each `y`,
  constant on the pairs `{x, x · y}`.
- **Against `3818b88f`:** with `∘` reversed, `3818b88f` implies T, but not the other way. `3818b88f`'s extra law
  fails on a 3-element model of T, and E saturates on it.
- **Models:** ∘ is even freer: 65,536 models on 4 elements, against `3818b88f`'s 1,024.
- **Shadow:** with `·` = `∘`, only one-element models remain.

So it is not identified, and weak. With `3818b88f` it forms the first two-member family of the
[families statistic](families.md). It is not a ledger row, because neither theory is identified. Memo:
[`notes/de0c0cf3.md`](../notes/de0c0cf3.md).

## `55cb2c91` (N1 rank 6): not identified, and the nearest thing to the jazz aim so far

- **The claim.** Two laws, `x · (x ∘ y) = x` and `x · y = ((y · z) · x) ∘ x`. Together they imply
  `(x · y) · y = x · y`.
- **Plain reading (E, both ways).** The theory is equivalent to `x · (y · z) = x · y`, `x · (x ∘ y) = x` and
  `x · y = (y · x) ∘ x`.
- **Structure (Lean `reduct_iff`).** The `·`-parts of its models are characterized exactly. `∘` acts as a partial
  swap `y · x ↦ x · y`: forced wherever the swap is defined, and free elsewhere.
- **Its one-operation shadow is trivial.** With `x · y = x ∘ y`, only one-element models are left.
- **Literature.** Related in pieces only: ETP Equations 327 and 378, and Waldhauser's idempotent case. No source was
  found for the whole theory.

Memo: [`notes/55cb2c91.md`](../notes/55cb2c91.md).

## `1d0a5211` (N1 rank 7): Stein's law split across two operations

- **The claim.** `x · (x ∘ y) = y ∘ x` and `(x ∘ (y · z)) ∘ z = z`.
- **Reading.** With one operation, the first law is Stein's first law, `x(xy) = yx` (ETP 335). The second law alone
  gives `(x · y) ∘ y = y`.
- **Synergy.** The emergent law `x · (x ∘ (y · x)) = x` takes two rewriting steps: real, but shallow.
- **Shadow.** With `x · y = x ∘ y`, only one-element models are left. Not identified.

Memo: [`notes/1d0a5211.md`](../notes/1d0a5211.md).

## `a9295908` (N1 rank 8): a fragment of Heyting algebras, reached from an odd angle

- **The claim.** `x · (x ∘ x) = x`, `(x ∘ y) · y = y` and `x · y = x ∘ (y · x)`.
- **Plain reading (E, both ways).** A commutative, idempotent `·` that need not be associative, with
  `x ∘ (x · y) = x · y` and `(x ∘ y) · y = y`.
- **Models.** Read `·` as ∧ and `x ∘ y` as `(y → x) → y`: every Heyting algebra is a model (Lean). On chains this `∘`
  is the strict-order connective of Gödel logic (Baaz, Ciabattoni and Zach, 2000).
- **Verdict.** Identified (ledger row 11). The search knew nothing of Heyting algebras.

Memo: [`notes/a9295908.md`](../notes/a9295908.md).

## `742cc445` (N1 rank 9): McKenzie's L1 with a non-lattice partner

- **The claim.** `x · (y ∘ (x ∘ z)) = x`, which is McKenzie's lattice law L1, and `x ∘ ((x ∘ y) · (z ∘ x)) = x`, which
  fails in the 2-element lattice.
- **Synergy.** Together they force one absorption law, idempotence of both operations and `x ∘ (x ∘ y) = x`. Neither
  law alone gives any of these (E).
- **∘ is never associative.** With ∘ associative, the theory collapses to `·` = `∘` (E). That rules out every
  band-based family: skew lattices, quasilattices, paralattices.
- **Literature.** No source found.

Memo: [`notes/742cc445.md`](../notes/742cc445.md).

## `97a7dfcf` (N1 rank 10): a nilpotent pair

- **Plain reading (E, both ways).** With 0 = `x · x`: `(x · y) · z = 0`, `x ∘ (y · z) = 0` and
  `x · (y ∘ x) = x ∘ y`.
- **Shadow.** With `·` = `∘` it is a null semigroup.
- **Literature.** No source found.

Memo: [`notes/97a7dfcf.md`](../notes/97a7dfcf.md). The light look at rank 6, `7ec7f8f5` (the same nilpotent family), is
in [`notes/n1_ranks4-6.md`](../notes/n1_ranks4-6.md).

## Other identifications

- **X5's top candidates** (ledger row 12). `·` is a Steiner loop, and `∘` is the same loop translated by a constant.
- **`31d6d970`.** One variety, found three times. With associativity it is exactly Leech's rectangular skew lattices.
- **`10c98c4b`.** Its core is a Δ-bijective pair, from the Yang–Baxter literature.

Next: [open problems](open-problems.md).
