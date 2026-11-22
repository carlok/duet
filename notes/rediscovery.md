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

Not rediscoveries, kept apart: the synergy pair ETP 55 + 100 (no source found), and the full `10c98c4b` theory (no
source found; `notes/10c98c4b.md`).

R1's systematic results are added below when computed.
