# Survivors

Claims (corpus-emergent laws) with no proof and no countermodel after: countermodel search to size 6 (z3,
grounded), E 3.2.5 `--auto` with 2M processed clauses / 300 s, Vampire 5.1.0 300 s with `-sa discount` and
with its default strategy. Produced by `python -m soup.sweep_open` and the Vampire pass in REPORT.md (21 Nov 2026).
32 claims in 12 theories.

| theory | laws | open claims |
|---|---|---|
| `00f017a6` | x · ((x · y) ∘ y) = x & x · ((y ∘ x) ∘ z) = x & x ∘ ((y · x) · z) = x & x ∘ ((x ∘ y) · y) = x | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `45b1f0fb` | x · x = x & x ∘ x = x & x · (x · (x ∘ y)) = x & x ∘ (x ∘ (x · y)) = x & ((x ∘ y) · y) · y = y & ((x · y) ∘ y) ∘ y = y | x · (x ∘ y) = x |
| `4ec6760a` | x · (x ∘ y) = x & (x · y) ∘ y = y & x · (y ∘ (x · y)) = x & ((x ∘ y) · x) ∘ y = y | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `513de1ad` | x · ((y ∘ z) ∘ (x · z)) = x & ((x ∘ y) · (x · z)) ∘ y = y | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `5e0dc923` | x · y = y · x & x ∘ y = y ∘ x & x · ((y ∘ x) · x) = x & x ∘ ((y · x) ∘ x) = x & (x · (x ∘ y)) · x = x & (x ∘ (x · y)) ∘ x = x | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `bbdd0d1c` | x · y = y · x & x ∘ y = y ∘ x & x · ((y ∘ x) · x) = x & (x ∘ (x · y)) ∘ x = x | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `cdf702b5` | x · x = x & (x ∘ y) · (z ∘ (z · x)) = x | x · (y · x) = x |
| `d25065b6` | x · (x · (x ∘ y)) = x & x ∘ (x ∘ (x · y)) = x & ((x ∘ y) · y) · y = y & ((x · y) ∘ y) ∘ y = y | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `e6403d7a` | x · (y ∘ (x · y)) = x & x · ((y ∘ x) ∘ z) = x & (x · (y · z)) ∘ y = y & ((x ∘ y) · x) ∘ y = y | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `f096b282` | x · x = x ∘ x & x · (y ∘ (y ∘ (x ∘ y))) = x & x ∘ (y · (y · (x · y))) = x & (((x ∘ y) ∘ x) ∘ x) · y = y & (((x · y) · x) · x) ∘ y = y | x · x = x; x ∘ x = x; x · (x · x) = x |
| `f5321de4` | x · ((x ∘ x) ∘ y) = x & x ∘ ((x · x) · y) = x & (x ∘ x) · (x ∘ x) = x & (x · x) ∘ (x · x) = x & (x ∘ (y ∘ y)) · y = y & (x · (y · y)) ∘ y = y | x · x = x; x ∘ x = x; x · x = x ∘ x |
| `f5e53602` | x · (y ∘ (y ∘ (x ∘ y))) = x & x ∘ (y · (y · (x · y))) = x & (((x ∘ y) ∘ x) ∘ x) · y = y & (((x · y) · x) · x) ∘ y = y | x · x = x; x ∘ x = x; x · x = x ∘ x |
