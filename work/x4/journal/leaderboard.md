# soup leaderboard

Updated 2026-11-22 15:31:51. Run x4: 0 searchers, 0 verifiers, queue 1320 pending / 6 stage c.
636 verified theories, 565 with positive score, 7 with open claims. Score = verified score (stages a/b, c when run); difficulty from z3 effort (z3-solver 5.4.1.0).

| # | score | key | arm | dualities | laws | proved emergent | refuted | open | models 2/3/4/5 | stage |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.774 | `94d69dd2` | fusion | - | x · (y · x) = y ∘ y & (x ∘ y) · x = y ∘ x & (x · x) · x = (y ∘ x) ∘ x | x · (y ∘ x) = x ∘ x (6.20); x · (x · x) = x · (y ∘ x) (4.80) | 0 | 0 | 0/0/8/1 | b |
| 2 | 1.450 | `3b3b1176` | fusion | - | x · (x · y) = x ∘ x & x · x = y ∘ (x ∘ y) & x · y = (y · x) ∘ y | x · x = x ∘ (y · x) (4.60); x · (x · x) = x ∘ (y · x) (5.00) | 1 | 0 | 0/0/7/1 | b |
| 3 | 1.295 | `7ec7f8f5` | fusion | - | x · (y ∘ x) = x ∘ y & x · (y · x) = (x · x) ∘ z & (x · y) · z = (z ∘ x) ∘ x | x · (y · x) = x ∘ (x · y) (8.80) | 0 | 0 | 0/1/8/1 | b |
| 4 | 1.141 | `700b8f93` | fusion | - | x · x = y · y & x · (y ∘ x) = x ∘ y & (x · y) · x = z · (z ∘ y) | (x ∘ y) · x = x · x (2.70); (x ∘ y) · x = x · (x · x) (4.70) | 0 | 0 | 0/0/8/1 | b |
| 5 | 1.046 | `f79a5097` | fusion | - | x · (y ∘ x) = x & x ∘ ((x ∘ y) · y) = x & x ∘ ((x · y) ∘ x) = x & x · ((y ∘ y) ∘ (y · x)) = x | x · (x ∘ y) = x (1.70); x · (x ∘ y) = x · x (1.90); x · (x · x) = x · (x ∘ y) (1.90) | 0 | 0 | 0/1/8/1 | b |
| 6 | 1.028 | `c73d174c` | fusion | - | x · (y · x) = y ∘ y & (x ∘ y) · x = y ∘ x & x · x = (x · (y · y)) ∘ x | x · (y ∘ x) = x · x (3.10); x · (x · x) = x · (y ∘ x) (3.40) | 0 | 0 | 0/0/8/1 | b |
| 7 | 0.911 | `5e83bbfa` | fusion | - | x · (x · y) = y · y & x · ((y ∘ y) · x) = x | (x ∘ x) · y = y (1.40); (x ∘ x) · y = y · y (1.20); (x ∘ x) · y = y · (y · y) (1.30) | 0 | 0 | 0/8/8/1 | b |
| 8 | 0.890 | `fff58b83` | fusion | - | x · y = y · x & x · x = y ∘ y & x · (y ∘ z) = x ∘ (z · y) & (x · y) ∘ y = (x ∘ z) ∘ x & x ∘ (y · (y ∘ x)) = y ∘ y | x · x = (x · y) ∘ x (3.10); x · (x · x) = (x · y) ∘ x (3.10) | 0 | 0 | 0/0/6/1 | b |
| 9 | 0.841 | `204aea15` | fusion | - | x · y = y · x & x · (y · x) = y ∘ y & (x · y) · z = y ∘ (x ∘ z) & (x · y) · x = (z ∘ y) ∘ y & (x ∘ y) · z = (y · x) ∘ z | x · (x · y) = x ∘ x (2.60); x · (x · x) = x · (x · y) (2.70) | 0 | 0 | 0/0/8/1 | b |
| 10 | 0.839 | `7c476118` | fusion | - | x · ((y ∘ x) ∘ z) = x & (x · y) ∘ (x ∘ y) = x | x · (x · y) = x (1.40); x · (x · y) = x · x (1.60); x · (x · x) = x · (x · y) (1.60) | 0 | 0 | 0/0/8/1 | b |
| 11 | 0.834 | `2c9e9108` | fusion | - | x · (y · z) = x ∘ x & (x ∘ y) · x = x · (x · z) & x · (x ∘ y) = (x ∘ x) ∘ z & (x · y) · z = y ∘ (x ∘ z) & (x ∘ y) · z = (y · x) ∘ z | (x · y) ∘ y = x ∘ x (2.40); x · (x · y) = x · (x ∘ y) (2.90) | 1 | 0 | 0/0/8/1 | b |
| 12 | 0.813 | `97a7dfcf` | fusion | - | x · x = y · y & x · (y ∘ x) = x ∘ y & (x · y) · z = y ∘ (z · y) | x · x = x ∘ (x · y) (2.50); x · (x · x) = x ∘ (x · y) (2.40) | 0 | 0 | 0/1/8/1 | b |
| 13 | 0.811 | `742cc445` | fusion | - | x · (y ∘ (x ∘ z)) = x & x ∘ ((x ∘ y) · (z ∘ x)) = x | x ∘ (x ∘ y) = x (1.20); x · x = x ∘ (x ∘ y) (1.40); x · (x · x) = x ∘ (x ∘ y) (1.40) | 0 | 0 | 0/3/8/1 | b |
| 14 | 0.807 | `a8963027` | fusion | - | x · (x · y) = x & x ∘ (y ∘ x) = x & x ∘ (y · (x · (x ∘ z))) = x | x ∘ (x · y) = x (1.40); x · x = x ∘ (x · y) (1.50); x · (x · x) = x ∘ (x · y) (1.50) | 0 | 0 | 0/0/8/1 | b |
| 15 | 0.784 | `3301abf0` | fusion | - | x · y = y · x & x · (y · x) = y ∘ y & (x · y) ∘ y = x ∘ (x · x) & (x · y) · z = y ∘ (x ∘ z) & (x ∘ y) · z = (y · x) ∘ z | x · (x · y) = x ∘ x (2.20); x · (x · x) = x · (x · y) (2.80) | 0 | 0 | 0/0/8/1 | b |
| 16 | 0.777 | `288d3f1b` | fusion | - | x · y = y · x & x · (y ∘ z) = x ∘ (z · y) & x · (y · z) = (x ∘ z) ∘ y & (x ∘ y) ∘ x = (z ∘ w) ∘ w & (x · y) ∘ (y · z) = x ∘ x | (x · y) · y = x ∘ x (2.40); x · (x · y) = x ∘ (y · y) (2.50) | 0 | 0 | 0/0/8/1 | b |
| 17 | 0.777 | `6c306a36` | fusion | - | x · y = y · x & x · x = y ∘ (y ∘ x) & (x ∘ y) ∘ y = z ∘ (w ∘ x) & (x · y) · z = (w ∘ z) · u | x · (x · y) = x · x (2.40); x · (x · x) = x · (x · y) (2.50) | 0 | 0 | 0/0/8/1 | b |
| 18 | 0.773 | `f1f50575` | fusion | - | x · y = y · x & x ∘ y = y ∘ x & x · (x ∘ x) = x ∘ x & x · (y ∘ z) = x ∘ (z · y) & x · (y · z) = (x ∘ z) ∘ y & (x · y) ∘ y = z ∘ (z ∘ z) | x · (x · y) = x ∘ x (2.90); x · (x · x) = x · (x · y) (3.40) | 0 | 0 | 0/0/4/1 | b |
| 19 | 0.763 | `33eca86a` | fusion | - | x · y = y · x & x · x = y ∘ (y · x) & x · (y ∘ z) = x ∘ (z · y) & x ∘ (x · y) = y ∘ (x ∘ z) & (x · y) · x = (y · y) ∘ z & (x · x) · y = (z ∘ y) ∘ x | x · (x · y) = x · x (2.40); x · (x · x) = x · (x · y) (2.40) | 0 | 0 | 0/0/8/1 | b |
| 20 | 0.746 | `d82738a2` | fusion | - | x · y = y · x & x · (y · x) = y ∘ (y ∘ z) & x · (y · z) = (x · w) ∘ w & x · x = (y ∘ (z ∘ x)) ∘ x | (x · y) · y = x · x (2.30); x · (x · y) = x ∘ (x ∘ y) (2.40) | 0 | 0 | 0/0/8/1 | b |
| 21 | 0.746 | `f584b45c` | fusion | - | x · y = y · x & x · (y · x) = y ∘ (y ∘ z) & x · (y ∘ x) = z ∘ (w ∘ y) & (x · x) ∘ y = (z ∘ y) ∘ z & x · x = (y ∘ (z ∘ x)) ∘ x | x · (x · y) = x · x (2.30); x · (x · x) = x · (x · y) (2.40) | 0 | 0 | 0/0/8/1 | b |
| 22 | 0.740 | `920ddd7d` | fusion | - | x · (y ∘ x) = x & x ∘ ((x ∘ y) · y) = x & ((x · y) · x) ∘ x = x | (x · y) · x = x (1.20); x · (x · y) = x · y (1.30); x · (x · y) = x · (y · y) (1.40) | 0 | 0 | 0/1/8/1 | b |
| 23 | 0.736 | `01085885` | fusion | - | x · (y ∘ x) = x ∘ y & (x · ((y · x) · z)) ∘ z = z | x ∘ (y · (y · x)) = x (1.80); x · x = x ∘ (y · (y · x)) (1.90) | 3 | 0 | 0/8/8/1 | b |
| 24 | 0.732 | `269b245d` | fusion | - | x · y = y · x & x · (y ∘ x) = z ∘ z & x · (y ∘ z) = x ∘ (z · y) & x ∘ (y · x) = z ∘ (x ∘ y) & x · (y · z) = (x ∘ z) ∘ y | x · (x · y) = x ∘ x (2.30); x · (x · x) = x · (x · y) (2.30) | 0 | 0 | 0/0/8/1 | b |
| 25 | 0.731 | `4de631a2` | fusion | - | x · ((x · y) · (z · z)) = y & x · (((y ∘ x) · x) ∘ y) = x & (x ∘ (x ∘ y)) ∘ (z ∘ z) = y | x · y = y · x (4.10); x · (x · x) = y · (x · y) (4.00) | 0 | 0 | 1/0/1/0 | b |
| 26 | 0.721 | `46182448` | fusion | - | x · y = y · x & x · x = x ∘ x & x · (y · y) = y · (x · z) & x ∘ (y ∘ z) = x ∘ (w ∘ z) & (x ∘ y) ∘ y = z ∘ (w · x) & (x ∘ y) ∘ x = (y ∘ z) ∘ z | x · (x · y) = x ∘ (x · y) (5.10) | 0 | 0 | 0/0/8/1 | b |
| 27 | 0.709 | `373c9183` | fusion | - | x · (x · y) = x & (x ∘ y) · (x · y) = x | x ∘ (x · y) = x (1.00); x · x = x ∘ (x · y) (1.20); x · (x · x) = x ∘ (x · y) (1.10) | 0 | 0 | 0/5/8/1 | b |
| 28 | 0.707 | `630ece20` | fusion | - | x · y = y · x & x ∘ y = y ∘ x & x · (y · z) = x · (w · z) & x · (y ∘ z) = (z · w) ∘ x & (x ∘ x) ∘ y = z ∘ (z ∘ w) & (x · x) · (x · x) = y · y | x · x = x ∘ (x · y) (3.70); x · (x · y) = x · (x ∘ y) (1.80) | 0 | 0 | 0/0/4/1 | b |
| 29 | 0.688 | `e45c2807` | fusion | - | x · (y · x) = x & (x · y) · x = x · y & ((x ∘ y) · y) ∘ y = y | x · (x · y) = x (0.90); x · (x · y) = x · x (1.10); x · (x · x) = x · (x · y) (1.00) | 0 | 0 | 0/8/8/1 | b |
| 30 | 0.685 | `374dcb40` | fusion | - | x · y = y · x & x ∘ (y ∘ z) = x ∘ x & x · (x ∘ y) = z ∘ (x ∘ w) & (x · y) · z = x ∘ (x · w) & (x · x) ∘ y = y ∘ (x ∘ x) | x · (x · y) = x ∘ x (2.20); x · (x · x) = x · (x · y) (2.10) | 0 | 0 | 0/0/8/1 | b |
