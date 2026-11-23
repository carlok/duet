# N1 ranks 4–6: light digs (23 Nov 2026, night; post hoc)

Script: `notes/dig_light.py <key>` (E, 20 s per law of order ≤ 3 suggested by the run's corpus, then the shadow with
x·y = x∘y, 30 s per law). Outputs: `notes/dig_742cc445.out`, `notes/dig_97a7dfcf.out`, `notes/dig_7ec7f8f5.out`. The
literature checks were done with N1's top 10 (`work/check/literature.json`). "False" in the outputs means E found no
proof in the budget, not a refutation.

## `742cc445` (X4, rank 4): half of McKenzie's lattice basis, with a mixed second law

- T = {x·(y∘(x∘z)) = x, x∘((x∘y)·(z∘x)) = x}. Law 1 is McKenzie's L1, identical as a law (`law_index`, checked).
- E proves 136 of the 138 suggested laws of order ≤ 3, and 129 of them are emergent. Among them:
  - the absorption law x·(x∘y) = x, and x·(y∘x) = x;
  - x·x = x, x∘x = x, x∘(x∘y) = x;
  - (x∘y)·x = x∘y, x·(y∘y) = x·y and x∘(y·y) = x∘y.
- Shadow: with x·y = x∘y, E proves x·y = x, so the shadow is the left-zero band.
- **Reading:** lattice and band territory, reached from one McKenzie law and a variant of another. Not identified.
  The obvious next check is the relation to skew lattices and to McKenzie's full basis. `soup.relabel` found none
  among the named theories.

## `97a7dfcf` (X4, rank 5): a nilpotent pair

- T = {x·x = y·y, x·(y∘x) = x∘y, (x·y)·z = y∘(z·y)}. The square x·x is a constant, call it 0.
- E proves all 97 suggested laws of order ≤ 3, 95 of them emergent. Every ·-product of three elements is 0, and so is
  y∘w whenever w is a ·-product.
- Shadow: commutative, associative and x(yz) = xy (E). Null semigroups satisfy it.
- **Reading:** a zeropotent, nilpotent-of-class-3 pair, which the earlier note relates to zeropotent algebras with
  x² = 0. Not identified.

## `7ec7f8f5` (X4, rank 6): the same nilpotent family

- T = {x·(y∘x) = x∘y, x·(y·x) = (x·x)∘z, (x·y)·z = (z∘x)∘x}. Its second law makes x·(y·x) independent of y and
  (x·x)∘z independent of z: X4's attractor in another form.
- Only 2 laws of order ≤ 3 are suggested, and neither is emergent; its off-diagonal law has order 4.
- Shadow: commutative, associative and x(yz) = xy (E); the earlier note has the collapse to a constant operation.
- **Reading:** not identified. It is in the nilpotent/constant region that X5's filter was built to leave.
