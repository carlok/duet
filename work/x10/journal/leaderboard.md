# soup leaderboard

Updated 2026-11-25 14:31:16. Run x10a: 0 searchers, 0 verifiers, queue 1500 pending / 157 stage c.
180 verified theories, 17 with positive score, 151 with open claims. Score = verified score (stages a/b, c when run); difficulty from z3 effort (z3-solver 5.4.1.0).

| # | score | key | arm | dualities | laws | proved emergent | refuted | open | models 2/3/4/5 | stage |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.031 | `23a4d276` | fusion4 | - | x · (x · y) = y · y & (x · ((y · y) · y)) ∘ x = x | (x · x) ∘ y = y (1.40); (x · (x · x)) ∘ y = y (1.50); (x · x) ∘ x = (y · y) ∘ x (1.60) | 0 | 0 | 0/8/8/1 | b |
| 2 | 0.582 | `cf580ad5` | fusion4 | - | x · (x ∘ y) = y ∘ (x · x) & (x · (y ∘ x)) · z = y · z & x · (x · ((x ∘ y) ∘ y)) = x & x ∘ ((y ∘ y) · (y ∘ x)) = y | x ∘ y = y ∘ x (8.20) | 0 | 1 | 0/0/1/0 | b |
| 3 | 0.355 | `cb74b7d9` | fusion4 | - | x · y = y · x & x · (y · z) = (y ∘ z) ∘ x & x ∘ (y · ((y · x) ∘ y)) = y | x ∘ y = y ∘ x (2.50) | 1 | 0 | 1/0/2/0 | b |
| 4 | 0.332 | `68c5926e` | fusion4 | - | (x ∘ x) · y = y · (x ∘ x) & (x ∘ x) · (x · (y · x)) = y & (x · (y ∘ x)) · (y · z) = z | x · (y · x) = y · (x · x) (3.90) | 0 | 1 | 0/1/1/1 | b |
| 5 | 0.254 | `35f25fc4` | fusion4 | - | x · y = y · x & x · (y · x) = y & ((x · x) ∘ x) · (x ∘ y) = y | x · (x · y) = y (1.00); x · (x · x) = y · (y · x) (0.90) | 0 | 0 | 1/0/2/1 | b |
| 6 | 0.239 | `7c2b9af9` | fusion4 | - | x · (y ∘ y) = y · x & x ∘ (((y ∘ x) · z) ∘ y) = x & (x ∘ (y · (y · y))) ∘ x = x | x ∘ ((y · x) ∘ x) = x (1.10) | 0 | 1 | 0/8/8/0 | b |
| 7 | 0.200 | `546a2327` | fusion4 | - | x · (x ∘ y) = y · x & x ∘ (((y · y) · y) ∘ x) = x & (x ∘ (y · (z ∘ x))) ∘ z = z | (x ∘ (x · y)) ∘ y = y (0.90) | 6 | 1 | 0/8/8/1 | b |
| 8 | 0.200 | `a3901315` | fusion4 | - | x · (y ∘ y) = y · x & x ∘ (((y · z) · z) ∘ x) = x & (x ∘ (y · (z ∘ x))) ∘ z = z | (x ∘ (x · y)) ∘ x = x (0.90) | 1 | 1 | 0/8/8/1 | b |
| 9 | 0.192 | `8ac8e509` | fusion4 | - | x · ((y ∘ z) ∘ z) = x · y & x ∘ ((x · x) ∘ (x · y)) = y & (x · (y · (x ∘ y))) · x = x | (x ∘ y) ∘ y = x (0.90) | 1 | 1 | 0/0/6/1 | b |
| 10 | 0.148 | `71a44d8f` | fusion4 | - | x · (x · y) = y & (x ∘ y) ∘ y = x & (x ∘ y) · x = y ∘ (y · y) | x · (x ∘ x) = y · (y ∘ x) (1.50) | 1 | 0 | 1/0/2/1 | b |
| 11 | 0.147 | `1e4fb949` | fusion4 | - | x · (y ∘ (y ∘ x)) = x & (x ∘ y) ∘ y = y ∘ (y ∘ x) & x · (y · (x · (y ∘ y))) = y | x · ((x ∘ y) ∘ y) = x (0.80) | 1 | 1 | 0/1/8/1 | b |
| 12 | 0.143 | `8dfbf0a5` | fusion4 | - | (x ∘ x) · (x ∘ y) = y & x ∘ (x ∘ ((y · z) · z)) = y | x · (y ∘ x) = y ∘ y (1.70) | 0 | 2 | 0/1/0/1 | b |
| 13 | 0.123 | `2ac6a9ad` | fusion4 | - | x · (y ∘ (x ∘ (y ∘ x))) = x & (x · y) · ((x · z) · y) = z & (x · (x ∘ (x · y))) ∘ x = y | x · (x · x) = y ∘ (x ∘ y) (2.90) | 0 | 1 | 0/0/1/0 | b |
| 14 | 0.085 | `f78e62c2` | fusion4 | - | x · x = x ∘ x & x · (x ∘ x) = x & (x ∘ y) · y = y · (x ∘ y) & (x ∘ ((y · y) ∘ z)) ∘ x = z & ((x · (y ∘ x)) ∘ x) · y = x | x · y = y · x (1.20) | 0 | 1 | 0/0/1/0 | b |
| 15 | 0.085 | `efdac149` | fusion4 | - | x · (y · x) = y & (x · y) · (z ∘ z) = y ∘ x | x · (x ∘ x) = y ∘ (y · x) (1.00) | 0 | 0 | 1/0/1/1 | b |
| 16 | 0.077 | `abb80efc` | fusion4 | - | x · y = y · x & (x ∘ y) · x = z · (y ∘ z) & x · ((x ∘ y) · (y · x)) = x | x · (x ∘ x) = y · (y ∘ x) (0.90) | 1 | 1 | 0/1/1/1 | b |
| 17 | 0.077 | `ecba77c9` | fusion4 | - | x · (x · y) = y & x ∘ (x ∘ y) = y & x · (x ∘ x) = (y · x) ∘ y | x · (x · y) = x ∘ (x ∘ y) (0.90) | 1 | 0 | 1/0/2/0 | b |
