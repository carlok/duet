# How this was made

[← README](../README.md)

An AI coding assistant (Claude Code, by Anthropic) designed, coded, ran and wrote most of this project, directed and
reviewed by the author. The commits carry `Co-Authored-By` trailers. [`CLAUDE.md`](../CLAUDE.md) is the assistant's
working memory: rules, code map, facts, and the pitfalls it ran into.

**No language model takes part in the search or its scoring** (rule 6 in `CLAUDE.md`). Language models were used
outside it in two ways:
- **Offline LLM work.** An external model worked on the 32 survivor claims, following
  [`prompts/README.md`](../prompts/README.md). Its answers count only after `soup.check_offline` verifies them.
- **Literature lookups.** Web-only AI agents searched the literature, and their key claims were rechecked by machine.

Every claim rests on prover proofs, finite models or Lean, never on a model's word. Deviations and slips are
disclosed in [`PREREGISTRATION.md`](../PREREGISTRATION.md) and [`REPORT.md`](../REPORT.md).

Next: [running it](running.md).
