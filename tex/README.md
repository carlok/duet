Draft paper. Build inside Podman:

    podman build -t soup-tex tex
    podman run --rm -v "$PWD/tex:/tex" soup-tex

Every number in the draft comes from `REPORT.md` (and through it from a script). Sections marked
`\pending{...}` wait for the tasks named there (T3, T4, ...).
