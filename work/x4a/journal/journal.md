# soup journal

Append-only. One section per run; times are UTC (container clock).

## 2026-11-22 12:55:23 · run x4 started

- budget 9000 s · 4 searchers (seeds 701–704, arm fusion) · 4 verifiers (v0 prefers stage c) · z3 5.4.1 · 11 cores
- before: 0 verified theories, 4252 found structures, queue 0 pending / 0 stage c
- 12:55:40 · `3c798d42` stage b · score **0.181** (cheap 8.018) · - · fusion · models 2/3/4/5 = 1/8/8/1 · v1 in 6s
  - laws: x · (x ∘ y) = x & (x ∘ ((x · y) ∘ x)) ∘ z = z
  - claims: x · ((x ∘ x) · y) = x false (size 3); (x · (y ∘ y)) · x = x · x false (size 3); x · (y ∘ ((y ∘ x) ∘ x)) = x false (size 4); x · ((x ∘ (x · x)) · y) = x false (size 3); x · ((x ∘ (x ∘ x)) · y) = x proved (effort 2,783)
- 12:55:40 · `9382b8c3` stage b · score **0.195** (cheap 47.229) · - · fusion · models 2/3/4/5 = 0/8/8/1 · v0 in 4s
  - laws: x · (y ∘ y) = x & (x · y) · y = x · x
  - claims: (x · y) · y = x · (y ∘ y) proved (effort 659)
- 12:55:42 · `12ca99fd` stage b · score **0.577** (cheap 53.938) · - · fusion · models 2/3/4/5 = 0/0/8/1 · v3 in 6s
  - laws: x · (y ∘ z) = y · y & (x ∘ y) · z = y ∘ (z ∘ z)
  - claims: x · x = y · y proved (effort 156,292); x · (x · x) = y · y proved (effort 38,570); x · (x · x) = x · (y · y) proved (effort 21,494)
- 12:55:46 · `924e8668` stage b · score **0.735** (cheap 106.000) · - · fusion · models 2/3/4/5 = 0/8/8/1 · v1 in 6s
  - laws: x · (x · y) = (y ∘ z) ∘ w & x · x = y ∘ ((x ∘ z) ∘ x)
  - claims: x · x = y · y proved (effort 16,682); x · (x · x) = y · y proved (effort 19,738); x · (x · x) = x · (x · y) proved (effort 11,113)
- 12:55:53 · **new #1**: `924e8668` score 0.735: x · (x · y) = (y ∘ z) ∘ w & x · x = y ∘ ((x ∘ z) ∘ x)
- 12:55:54 · `03c40daf` stage b · score **0.543** (cheap 68.466) · - · fusion · models 2/3/4/5 = 0/1/8/1 · v1 in 8s
  - laws: x · y = y · x & x · (y · z) = (x ∘ w) ∘ u & x ∘ ((y · z) ∘ z) = z ∘ z
  - claims: x ∘ x = y ∘ y proved (effort 29,381); x · (x · x) = y ∘ y proved (effort 50,862); x · (x · x) = y · (x · x) proved (effort 15,870)
- 12:56:15 · `23e00c92` stage b · score **0.362** (cheap 60.139) · - · fusion · models 2/3/4/5 = 1/0/1/0 · v1 in 21s
  - laws: x · (y ∘ z) = (z · x) ∘ y & (x ∘ y) · ((x · y) ∘ z) = z
  - claims: x · x = y · y proved (effort 481,272); x · (x · x) = x · (y · y) proved (effort 271,123)
- 12:56:37 · `e0f21a55` stage b · score **0.961** (cheap 79.094) · - · fusion · models 2/3/4/5 = 0/8/8/1 · v3 in 54s
  - laws: x · (y · x) = y · y & x · (x · y) = (y ∘ z) ∘ w & x · x = y ∘ ((x ∘ z) ∘ x)
  - claims: x · x = y · y proved (effort 10,601); x · (x · x) = y · y proved (effort 7,949); x · (x · x) = x · (x · y) proved (effort 13,774)
- 12:56:40 · `19b5765e` stage b · score **1.253** (cheap 122.080) · - · fusion · models 2/3/4/5 = 0/0/8/1 · v1 in 25s
  - laws: x · y = y · x & x · (y · z) = (x ∘ z) ∘ z & x · x = y ∘ (y · (x · x))
  - claims: x · x = y · y proved (effort 22,434); x · (x · x) = y · y proved (effort 5,332,842); x · (x · x) = x · (x · y) proved (effort 1,090)
- 12:56:40 · **new #1**: `19b5765e` score 1.253: x · y = y · x & x · (y · z) = (x ∘ z) ∘ z & x · x = y ∘ (y · (x · x))
- 12:56:45 · `f1698cd5` stage b · score **0.773** (cheap 44.552) · - · fusion · models 2/3/4/5 = 0/0/8/1 · v2 in 61s
  - laws: x · ((y ∘ x) ∘ z) = x & x ∘ (x ∘ (y ∘ x)) = y ∘ y & (x · (y · (y · y))) · x = y
  - claims: x · x = y · y proved (effort 2,937,867); x · x = (y · y) ∘ y proved (effort 2,477,270); x · (x · x) = x · (y · y) proved (effort 8,598,845)
- 12:56:47 · `3f48fbc2` stage b · score **0.214** (cheap 127.600) · - · fusion · models 2/3/4/5 = 0/2/8/1 · v1 in 7s
  - laws: x · y = y · x & x · x = x ∘ (y ∘ y) & (x · y) · z = (z ∘ w) ∘ y
  - claims: x · (x · x) = x · (x · y) proved (effort 213,111)
- 12:56:49 · `3add215d` stage b · score **0.324** (cheap 92.902) · - · fusion · models 2/3/4/5 = 0/2/8/1 · v2 in 4s
  - laws: x · y = y · x & x · (x · y) = x · x & x · (y · z) = x ∘ (x ∘ z) & x · x = (y ∘ (y ∘ y)) ∘ x
  - claims: x · (y · y) = x · x proved (effort 28,448); x · (x · x) = x · (y · y) proved (effort 8,736)
- 12:56:52 · `1ec877d3` stage b · score **1.238** (cheap 88.411) · - · fusion · models 2/3/4/5 = 0/2/8/1 · v1 in 5s
  - laws: x · y = y · x & x · x = x ∘ (y ∘ x) & (x ∘ y) · y = x · (x ∘ y) & x · x = ((y · x) ∘ z) ∘ y
  - claims: x · x = y · y proved (effort 69,799); x · (x · x) = y · y proved (effort 158,929); x · (x · x) = x · (y · y) proved (effort 22,178)
- 12:56:57 · `69431715` stage b · score **0.722** (cheap 100.875) · - · fusion · models 2/3/4/5 = 0/0/8/1 · v1 in 5s
  - laws: x · y = y · x & x · (x · y) = x · x & (x · x) · y = x ∘ x & (x ∘ y) ∘ y = x ∘ (x ∘ z)
  - claims: x · x = y · y proved (effort 3,735); x · (x · x) = y · y proved (effort 15,160); x · (x · x) = x · (y · x) proved (effort 1,276)
- 12:57:05 · `46d2c4ce` stage b · score **0.780** (cheap 62.432) · - · fusion · models 2/3/4/5 = 0/0/8/1 · v1 in 8s
  - laws: x · y = y · x & x · (y · z) = (x ∘ w) ∘ u & ((x · x) · y) · y = x · x
  - claims: x · x = y · y proved (effort 3,336); x · (x · x) = y · y proved (effort 5,457); x · (x · x) = y · (x · x) proved (effort 9,447)
- 12:57:11 · `a205b036` stage b · score **0.840** (cheap 82.475) · - · fusion · models 2/3/4/5 = 0/1/8/1 · v1 in 5s
  - laws: x · (y · x) = x · x & x · (x ∘ y) = y ∘ y & (x ∘ x) · y = y · (z ∘ x) & (x · y) ∘ x = z ∘ (w ∘ x)
  - claims: x · x = y · y proved (effort 4,904); x · (x · x) = y · y proved (effort 16,076); x · (x · x) = x · (y · y) proved (effort 8,644)
- 12:57:29 · rebalance: 1687 competitive pending (priority >= 0.000) > 16: retired searcher s701, started verifier v4
- 12:58:18 · stopped by signal
