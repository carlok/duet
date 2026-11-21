# duet: search for synergy between two binary operations (Python package `soup`)

Everything runs inside a container; nothing is installed on the Mac. Data stays in `work/`
(mounted at `/data`); code is in the `soup/` package, copied into the image.

    cd ~/tmp/soup
    podman build -t soup .
    podman run --rm -v "$PWD/work:/data" soup bash run.sh test            # builds the matrix first if missing
    podman run --rm -v "$PWD/work:/data" soup bash run.sh stream --budget 3600

The streaming search starts 3 search and 8 verifier processes (rebalanced by queue length) and writes:

- `work/journal/journal.md`: what happened, in order (runs, notable verified theories, rebalancing, status)
- `work/journal/leaderboard.md`: top verified theories, rewritten every 15 s
- `work/logs/stats.jsonl`: one line per 15 s (queue, results, corpus, memory per process)
- `work/results/<key>.json`: one verified theory per file; `work/corpus/`: every structure found

See `CLAUDE.md` for the project rules and the task list, `REPORT.md` for numbers.
