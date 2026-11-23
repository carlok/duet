# Open problems

[← README](../README.md)

Each one defeated E, Vampire, Prover9 and finite-model search in our budgets. A proof, a finite countermodel, or an
infinite one with a checkable construction settles it.

## S12

Do `x·(y∘(y∘(x∘y))) = x`, `x∘(y·(y·(x·y))) = x`, `(((x∘y)∘x)∘x)·y = y` and `(((x·y)·x)·x)∘y = y` imply
`x·x = x∘x`?
- They do not imply `x·x = x`: a 10-element model refutes it (`tests/test_round2.py`). That model satisfies
  `x·x = x∘x`.
- No model on 2–6 elements has `x·x ≠ x`.
- Neither Vampire FMB nor Mace4 finds a countermodel to `x·x = x∘x` on ≤ 6 elements.
- E, Vampire, Prover9 and Twee found no proof. The longest runs were 2 h each (23 Nov 2026, REPORT "T6").
- With `x·y = x∘y` the laws become ETP Equations 437 and 3115. Whether they imply `x = x◇x` is also open.

## Infinite-only non-implications

A–D, S1, S9 and S11 in [`REPORT.md`](../REPORT.md). Their countermodels are certified, but they are necessarily
infinite. They are candidates for the TPTP library's non-theorem problems.

## A conjunction

ETP 55 ∧ 100 implies `x = x◇x`, though neither law does alone (E: 10 steps). The order-≤ 2 conjunction census on
the Lean Zulip does not cover it. Is it recorded somewhere?

Next: [how this was made](how-made.md).
