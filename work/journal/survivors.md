# Survivors

Claims (corpus-emergent laws) with no proof and no countermodel after: countermodel search to size 6 (z3,
grounded), E 3.2.5 `--auto` with 2M processed clauses / 300 s, Vampire 5.1.0 300 s with `-sa discount` and
with its default strategy. Produced by `python -m soup.sweep_open` and the Vampire pass in REPORT.md (21 Nov 2026).
32 claims in 12 theories.

**Correction (21 Nov 2026, evening).** The size-6 search was not complete: z3 ran out of budget at size 6 for
`00f017a6`, `45b1f0fb`, `5e0dc923`, `bbdd0d1c`, `d25065b6`, `e6403d7a` and at sizes 5 and 6 for `513de1ad`,
`f096b282`, `f5e53602` (`cm_unknown_sizes` in `work/results/`). None of the 12 theories reached stage c, so
Mace4 never ran on them. Several Vampire runs of the sweep were OOM-killed (2–4.4 GB, kernel log) rather than
timed out. `513de1ad` has a 5-element countermodel. See REPORT.md for the follow-up.

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
