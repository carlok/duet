# Candidates studied closely

[← README](../README.md)

Each has a memo in [`notes/`](../notes). Identifications go into the ledger
[`notes/rediscovery.md`](../notes/rediscovery.md). None of these theories is claimed new.

## `55cb2c91` (N1 rank 1): not identified, and the nearest thing to the jazz aim so far

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

## `1d0a5211` (N1 rank 2): Stein's law split across two operations

- **The claim.** `x · (x ∘ y) = y ∘ x` and `(x ∘ (y · z)) ∘ z = z`.
- **Reading.** With one operation, the first law is Stein's first law, `x(xy) = yx` (ETP 335). The second law alone
  gives `(x · y) ∘ y = y`.
- **Synergy.** The emergent law `x · (x ∘ (y · x)) = x` takes two rewriting steps: real, but shallow.
- **Shadow.** With `x · y = x ∘ y`, only one-element models are left. Not identified.

Memo: [`notes/1d0a5211.md`](../notes/1d0a5211.md).

## `a9295908` (N1 rank 3): a fragment of Heyting algebras, reached from an odd angle

- **The claim.** `x · (x ∘ x) = x`, `(x ∘ y) · y = y` and `x · y = x ∘ (y · x)`.
- **Plain reading (E, both ways).** A commutative, idempotent `·` that need not be associative, with
  `x ∘ (x · y) = x · y` and `(x ∘ y) · y = y`.
- **Models.** Read `·` as ∧ and `x ∘ y` as `(y → x) → y`: every Heyting algebra is a model (Lean). On chains this `∘`
  is the strict-order connective of Gödel logic (Baaz, Ciabattoni and Zach, 2000).
- **Verdict.** Identified (ledger row 11). The search knew nothing of Heyting algebras.

Memo: [`notes/a9295908.md`](../notes/a9295908.md).

## N1 ranks 4–6: light looks

- **`742cc445`.** Its first law is L1 of McKenzie's lattice basis. It proves absorption and idempotence, and its
  shadow is the left-zero band.
- **`97a7dfcf` and `7ec7f8f5`.** A nilpotent family: constant squares, and vanishing products.

Memo: [`notes/n1_ranks4-6.md`](../notes/n1_ranks4-6.md).

## Other identifications

- **X5's top candidates** (ledger row 12). `·` is a Steiner loop, and `∘` is the same loop translated by a constant.
- **`31d6d970`.** One variety, found three times. With associativity it is exactly Leech's rectangular skew lattices.
- **`10c98c4b`.** Its core is a Δ-bijective pair, from the Yang–Baxter literature.

Next: [open problems](open-problems.md).
