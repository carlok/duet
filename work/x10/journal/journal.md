# soup journal

Append-only. One section per run; times are UTC (container clock).

## 2026-11-25 13:52:25 · run x10a started

- budget 7200 s · 6 searchers (seeds 1401–1406, arm fusion4) · 4 verifiers (v0 prefers stage c, at most 2 stage-c tasks at once, none started in the last 3600 s) · z3 5.4.1 · 11 cores
- before: 156 verified theories, 16826 found structures, queue 1 pending / 156 stage c
- 13:53:34 · `23a4d276` stage b · score **1.031** (cheap 2.703) · - · fusion4 · models 2/3/4/5 = 0/8/8/1 · v0 in 12s
  - laws: x · (x · y) = y · y & (x · ((y · y) · y)) ∘ x = x
  - claims: (x · x) ∘ y = y proved (E steps 14); (x · (x · x)) ∘ y = y proved (E steps 15); (x · x) ∘ x = (y · y) ∘ x proved (E steps 16)
- 13:53:46 · **new #1**: `23a4d276` score 1.031: x · (x · y) = y · y & (x · ((y · y) · y)) ∘ x = x
- 13:58:31 · status: 5 verified this run (2 positive), queue 1502 pending / 4 claimed / 154 stage c (1504 competitive at >= 0.000, 949 dropped), 4 unremarkable results not listed, corpus 16853 found structures, 235,577 surrogate evaluations, PSS total 4492 MB
- 14:04:41 · status: 5 verified this run (2 positive), queue 1501 pending / 4 claimed / 154 stage c (1503 competitive at >= 0.000, 2555 dropped), 4 unremarkable results not listed, corpus 16853 found structures, 531,895 surrogate evaluations, PSS total 4569 MB
- 14:07:41 · `103d248b` stage b · score **0.000** (cheap 24.833) · - · fusion4 · models 2/3/4/5 = 1/0/2/0 · v0 in 618s
  - laws: x · (x ∘ ((y ∘ y) · y)) = y & (x · y) ∘ (z ∘ (x · z)) = y
  - claims: x · y = y · x unknown; x · (x · x) = y · (x · y) unknown
- 14:10:45 · status: 6 verified this run (2 positive), queue 1501 pending / 4 claimed / 155 stage c (1507 competitive at >= 0.000, 3536 dropped), 4 unremarkable results not listed, corpus 16855 found structures, 804,249 surrogate evaluations, PSS total 4662 MB
- 14:11:10 · `71a44d8f` stage b · score **0.148** (cheap 27.139) · - · fusion4 · models 2/3/4/5 = 1/0/2/1 · v0 in 208s
  - laws: x · (x · y) = y & (x ∘ y) ∘ y = x & (x ∘ y) · x = y ∘ (y · y)
  - claims: x · y = y · x false (size 5); x · (x ∘ x) = y · (y ∘ x) proved (E steps 15)
- 14:16:53 · status: 13 verified this run (4 positive), queue 1500 pending / 4 claimed / 155 stage c (1501 competitive at >= 0.000, 4251 dropped), 10 unremarkable results not listed, corpus 16862 found structures, 1,067,284 surrogate evaluations, PSS total 5175 MB
- 14:19:11 · `35f25fc4` stage b · score **0.254** (cheap 26.000) · - · fusion4 · models 2/3/4/5 = 1/0/2/1 · v0 in 212s
  - laws: x · y = y · x & x · (y · x) = y & ((x · x) ∘ x) · (x ∘ y) = y
  - claims: x · (x · y) = y proved (E steps 10); x · (x · x) = y · (y · x) proved (E steps 9)
- 14:23:07 · status: 22 verified this run (5 positive), queue 1500 pending / 4 claimed / 155 stage c (1501 competitive at >= 0.000, 4820 dropped), 18 unremarkable results not listed, corpus 16863 found structures, 1,338,188 surrogate evaluations, PSS total 5397 MB
- 14:25:13 · `cb74b7d9` stage b · score **0.355** (cheap 23.784) · - · fusion4 · models 2/3/4/5 = 1/0/2/0 · v0 in 281s
  - laws: x · y = y · x & x · (y · z) = (y ∘ z) ∘ x & x ∘ (y · ((y · x) ∘ y)) = y
  - claims: x ∘ y = y ∘ x proved (E steps 25); x · (x · x) = y · (x · y) false (size 9, linear model over Z/9)
- 14:29:20 · status: 24 verified this run (6 positive), queue 1502 pending / 4 claimed / 155 stage c (1503 competitive at >= 0.000, 5337 dropped), 19 unremarkable results not listed, corpus 16864 found structures, 1,618,328 surrogate evaluations, PSS total 5488 MB
- 14:30:57 · memory rule: 642 MB available < 1000 MB after 2313 s: stopping workers

### 2026-11-25 14:31:16 · run x10a ended

- 24 theories verified (6 positive score, 0 through stage c), 2 claims still open
- stage-c tasks cut by the stop and put back: 2
- 1,684,503 surrogate evaluations; 38 structures added to the corpus
- queue left: 1500 pending, 157 stage c (kept for the next run)
- top score overall 1.031; see leaderboard.md
