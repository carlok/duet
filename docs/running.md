# Running it, and where to look

[← README](../README.md)

Everything runs inside Podman, and nothing is installed on the host. The code is the `soup/` package. Data lives in
`work/`, mounted at `/data`.

    podman build -t soup .
    podman run --rm -v "$PWD/work:/data" soup bash run.sh test            # builds the matrix first if missing
    podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 3600

The image carries z3 5.4.1 and five provers built from pinned sources: E 3.2.5, Vampire 5.1.0, Prover9/Mace4
LADR-2026-8A and Twee 2.7.1. A stream run writes:
- `work/journal/`: the journal and the leaderboard;
- `work/results/`: one verified theory per file;
- `work/corpus/`: every structure found.

After each run's checks, two commands refresh the live tables: `soup.novelty --readme docs/ranking.md`, then
`soup.funnel --readme README.md` (commands in `CLAUDE.md`).

## Where to look

- **[`REPORT.md`](../REPORT.md):** results, newest first, each with its command and caveats.
- **[`PREREGISTRATION.md`](../PREREGISTRATION.md):** the plans fixed before each run, and the deviations.
- **[`notes/`](../notes):** analysis scripts and memos. Start with [`notes/rediscovery.md`](../notes/rediscovery.md),
  the ledger of everything that turned out to be known, and
  [`notes/candidates_table.md`](../notes/candidates_table.md).
- **[`lean/`](../lean):** Lean 4 certificates and general proofs.
- **[`tex/`](../tex):** the draft paper. **[`intro/`](../intro):** the introduction.
- **[`CLAUDE.md`](../CLAUDE.md):** the assistant's rules, code map and task list.
