# Offline prompts

Prompts for an LLM *outside* the search (rule 6: no LLM in the scoring loop).

- The LLM gets the prompt and an empty output directory **outside this repository and outside `work/`**,
  e.g. `$OFFLINE/<prompt>-<model>-<date>/` (`$OFFLINE`: a scratch directory of your choice). Containers never mount that path, so the search,
  the corpus and the scores cannot see it.
- Nothing it writes is trusted. Each item is checked by a program before it is reported (proof chains:
  every step proved by E/Vampire; finite models: checked with `law_vector`; rewrite systems:
  `soup.confluence`). Results enter `REPORT.md` only as "found offline with an LLM, machine-checked", in
  their own table, and never enter `work/results`, the corpus or the archive.
- `survivors.md`: the 32 open claims in 12 theories after the E/Vampire sweep of 21 Nov 2026.
