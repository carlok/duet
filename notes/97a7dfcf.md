# `97a7dfcf` (X4; N1 rank 5): a nilpotent pair

Status: **candidate, not identified**. Checks: `notes/97a7dfcf_checks.py` parts 1–2 (single-threaded E), output
`notes/97a7dfcf_checks.out`.

T = {x·x = y·y, x·(y∘x) = x∘y, (x·y)·z = y∘(z·y)}.

## Plain reading (E, both ways)

Write 0 for the constant x·x. T is equivalent to:
- x·x = 0;
- (x·y)·z = 0;
- x∘(y·z) = 0;
- x·(y∘x) = x∘y.

So a product whose left factor is a ·-product vanishes, and so does ∘ with a ·-product on its right. T also proves
(x·y)∘z = 0, x∘(y∘z) = 0 and (x∘y)∘z = 0. It does not prove x·(y·z) = 0, x·y = 0 or x∘y = 0 (E, 30 s each).

## Shadow and models

- With x·y = x∘y, T proves x·y = z·z: a null semigroup.
- With · = ∘ the laws are ETP Equations 40, 325 and 4453 (dossier).
- Non-degenerate models: 0 on 2 elements, 1 on 3, 22 on 4, ≥ 741 on 5 (dossier).

## Reading

T is a two-operation nilpotent structure: almost all products of depth 2 are 0, and x·(y∘x) = x∘y is the one non-zero
link between the operations. The earlier literature note relates it to zeropotent algebras (x² = 0). No source was
found for T. Not identified.
