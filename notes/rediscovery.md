# Rediscovery ledger (started 22 Nov 2026)

Every case where something the search found turned out to be already known, or a disguise of something known. For
each: what it is, how it was identified, and how long that took. Times are UTC, taken from commit times. The search
and its score never read this file (rule 6). R1 (PREREGISTRATION.md) measures rediscovery systematically against a
fixed catalogue; this ledger records the cases one by one, including those R1 cannot see.

Routes:
- **automatic**: a pipeline check (`soup.fragments`, `soup.split`, `soup.relabel`, `soup.hidden`, `soup.rediscover`);
- **prover**: an E equivalence written by hand for one candidate;
- **literature**: web search, zbMATH, papers, a delegated lookup. Literature work is done outside the search, by us
  with an LLM, and counts only after a source is read or a machine check passes.

| # | Found by the search | Turned out to be | Route | Source | Time to identification |
| --- | --- | --- | --- | --- | --- |
| 1 | L1 x·(y∘(x∘z)) = x and L2 x∘(y·(x·z)) = x (first sessions) | two of the four laws of McKenzie's 1970 lattice basis | literature | McKenzie 1970, via Veroff's lattice-basis page | about a day (found in the cloud sessions, identified 21 Nov morning) |
| 2 | 330 of T4's 998 prior-arm theories | fragments of the named theories, nearly all of lattices | automatic (`soup.fragments`) | T3's named list | at the end of the run |
| 3 | `4dc33674` and 12 more of the 81 candidates | split: a ·-theory and a ∘-theory side by side, bridges in disguise | automatic (`soup.split`, written for this on 22 Nov) | none needed | about 1–5 h after verification (the check did not exist before 02:35) |
| 4 | `8a512957`, `977c3603` | idempotent left quasigroups with ∘ written as the division | automatic (`soup.relabel`), then a prover equivalence | standard notion | about 1–5 h (the check did not exist before 02:38) |
| 5 | `1ca933c1`, `3078949b`, `87137d88` | subvarieties of the absorption pairs | automatic (`soup.relabel`) | T3's named list | same night |
| 6 | `10c98c4b`'s core B = {(x·y)∘(y·x) = x, (x∘y)·(y∘x) = x} | Δ-bijective algebras with their dual operation, from the Yang–Baxter literature | prover (B isolated by E, 04:20), then literature (06:21) | Bonatto, Kinyon, Stanovský, Vojtěchovský, arXiv:1910.02148, Lemma 2.10; Rump 2005 | about 3 h after verification. The first literature pass looked only at Latin squares and missed it. |

| 7 | `69dfbd8e` (X2, rank 3) | the variety of `2dc27508` (rank 10, from the earlier runs), axiomatized differently | prover: the two convergent presentations had the same 10 rules, then E both ways | none needed | about 40 min after X2 ended. The ranking had not noticed: it deduplicates only up to the dualities. |
| 8 | `3e068fa6` (X2, rank 11) = {(x∘y)·(y∘x) = y, x·x = x, x∘x = x} | half of the Δ-bijective core (relabelled), plus idempotence; its finite models are Δ-bijective pairs | prover (E's 3-rule presentation), then the argument "injective on a finite set means bijective" | as row 6 | about 40 min after X2 ended |
| 9 | `31d6d970` (X3, rank 3) = {x·(x∘y) = x, (x∘y)·y = y, (x·x)·(y·x) = x, (x·y)·(x·x) = x} | its associative case is a rectangular band with ∘ the transpose, which is term-equivalent to the rectangular skew lattices; laws 1–2 are Leech's absorptions a∧(a∨b) = a, (b∨a)∧a = a | literature (web-only agent: Leech's book, Prop. 1.3.14), then E both ways (`notes/31d6d970_checks.py`) | Leech 2020, Zbl 1530.06001 | about 50 min after X3 ended (11:08 → 12:00 UTC) |
| 10 | `31d6d970` (X3), `69dfbd8e` (X2) and `2dc27508` (the early runs) | one variety, reached three times from different axioms. Row 9's identification covers all three. | automatic (`soup.dedupe`, 18:10 UTC), rechecked by E both ways under rev∘ and rev·, with equal model counts on 3 and 4 elements | none needed | rows 7 and 9 had two of the three; dedupe joined them about 7 h after X3 |

Not rediscoveries, kept apart: the synergy pair ETP 55 + 100 (no source found), and the full `10c98c4b` theory (no
source found; `notes/10c98c4b.md`). The full `31d6d970` theory is not associative (both associativity laws fail in
its 3-element model) and has no source found. It is a non-associative weakening of rectangular skew lattices, much as
Fried's weakly associative lattices weaken lattices. Zelinka's anticommutative conservative groupoids, with ∘ their
transpose, are models.

## R1 (22 Nov 2026, 08:31 UTC; REPORT.md, R1)

Against a catalogue of 13 entries fixed in advance, the search rediscovered 7: lattice, skew lattice, absorption
pair, bisemilattice, idempotent left and right quasigroups, and weakly associative lattices. That is also 7 of the
12 entries that were not added post hoc. Exact equivalences:
- 12 different bases for lattices;
- 17 axiomatizations of absorption pairs;
- 3 of Fried's weakly associative lattices (X1; that name was not on T3's list).

All of these were found by an automatic check (`soup.rediscover`). Of the 99 top candidates, 44 are identified by
an automatic route: split, division, or a catalogue relation. The ledger rows above are the cases that needed a
prover by hand or the literature.
