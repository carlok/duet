An introduction to the project from scratch: sets and functions, binary operations, laws, theories and models,
synergy, and how the search works. Two versions of one text:

- `intro-reading.pdf` (`intro-reading.tex`): the text alone, for a first read; no exercises, no solutions.
- `intro.pdf` (`intro.tex`): the same text with exercises at the end of each section and solutions in an appendix.

The text is in `intro.tex` and the exercises in `exercises.tex`; `intro-reading.tex` only switches the version.

Build both inside Podman with the paper's image:

    podman build -t soup-tex tex
    podman run --rm -v "$PWD/intro:/tex" soup-tex

`checks.py` computes every numeric answer in the solutions (`podman run -i --rm soup python3 - < intro/checks.py`,
output in `checks.out`).
