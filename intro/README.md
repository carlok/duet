An introduction to the project from scratch: sets and functions, binary operations, laws, theories and models,
synergy, and how the search works. Two versions from one source (`intro.tex`, with the exercises in `exercises.tex`):

- `intro-reading.pdf`: the text alone, for a first read; exercises and solutions in two appendices at the end.
- `intro.pdf`: the same text with exercises at the end of each section; solutions in an appendix.

Build both inside Podman with the paper's image:

    podman build -t soup-tex tex
    podman run --rm -v "$PWD/intro:/tex" soup-tex

`checks.py` computes every numeric answer in the solutions (`podman run -i --rm soup python3 - < intro/checks.py`,
output in `checks.out`).
