# `de0c0cf3` (X7; N1 rank 2): a TS-quasigroup with ∘ constant on orbits, a weaker relative of `3818b88f`

Status: **candidate, not identified**, and a weak one. It is a proper supervariety of `3818b88f` (with ∘ reversed),
and its ∘ is even freer. Checks: `notes/de0c0cf3_checks.py` parts 1–2 (E, 30–60 s per goal; models on
TS-quasigroups with n ≤ 4), output `notes/de0c0cf3_checks.out`. 24 Nov 2026.

T = { x·(x·y) = y, (x·y)∘y = x∘y, (((x·x)∘x)·y)·y = x }.

## Structure (E)

- **· is a totally symmetric quasigroup.** T proves x·y = y·x, and with x·(x·y) = y also (x·y)·y = x.
- **∘ is idempotent:** T proves x∘x = x. T also proves (x·x)∘x = x and (x·y)∘x = y∘x.
- **Plain reading, E both ways.** T is equivalent to K = { x·y = y·x, x·(x·y) = y, x∘x = x, (x·y)∘y = x∘y }.
  - For each y, the map x ↦ x·y is an involution. Its orbits are the pairs {x, x·y}.
  - ∘(−, y) is constant on each orbit, and y∘y = y. Nothing else constrains ∘.
- **Against `3818b88f`** (the relabelling that reverses ∘):
  - `3818b88f` implies T (E).
  - T does not imply `3818b88f`'s extra law, which reads x∘(x·x) = x after the reversal. E saturates
    (CounterSatisfiable).
  - Finite witnesses on 3 and 4 elements confirm it: T holds, x∘(x·x) = x fails, checked with `law_vector`.
  - So `3818b88f` is a proper subvariety of T, read with ∘ reversed. This explains why `soup.dedupe` (equivalence
    only) and X7's known-library skip (fragments and subvarieties of *known* entries only) let T through.
- **Not implied** (E saturates): x·x = x, x·x = y·y, commutativity or associativity of ∘, x∘(x·y) = x∘y,
  (x∘y)∘y = x∘y, x∘(x∘y) = x∘y, and either projection.
- **Shadow:** with x·y = x∘y, T proves x·y = x and x·y = y, so only one-element models remain (E).

## Models

On every labelled TS-quasigroup with n ≤ 4, the ∘ that satisfy K number:

| n | TS-quasigroups | ∘ satisfying K | of them non-degenerate | of them also x∘(x·x) = x (`3818b88f`) |
|---|---:|---:|---:|---:|
| 2 | 2 | 4 | 2 | 2 |
| 3 | 3 | 81 | 78 | 29 |
| 4 | 16 | 65,536 | 65,520 | 1,024 |

The last column reproduces `3818b88f`'s counts (`notes/3818b88f_models.out`: 2, 29, 1,024), as it should. Each
sampled model satisfies T's own laws (758 checked).

## Reading

T is a totally symmetric quasigroup together with, for each y, an arbitrary function on the pairs {x, x·y}, with
y∘y = y. On 4 elements almost any such choice is a model: 4,096 per TS-quasigroup.
- The synergy is real but shallow. Commutativity of · and idempotence of ∘ need the second and third laws together.
- The fusion adds little structure. As with `3818b88f`, an expert may well say "a triple system plus a free choice".
- The two candidates form the first two-member family in the F1 statistic (`docs/families.md`): a TSQ, with an
  idempotent ∘ constant on the blocks.

## Literature

Nothing beyond `3818b88f`'s search (`notes/x6_top4.md`): the closest source is still Drápal, Griggs and Kozlik,
"Triple systems and binary operations" (Discrete Math. 325, 2014), read only as an abstract. It has one operation per
triple system, not a second one constant on the blocks. No source was found. That is weak evidence, but the reading
above makes a dedicated source unlikely to matter.
