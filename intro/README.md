An introduction to the project from scratch, in two documents:

- **`intro.pdf`** (`intro.tex`, 9 pages): the text. It covers sets and functions, binary operations, laws, theories
  and models, synergy, how the search works, and what it has found. It has definitions, examples, theorems and
  proofs, and nothing else.
- **`exercises.pdf`** (`exercises.tex`, 4 pages): exercises arranged by the sections of the text, with solutions.
  The exercises of Section n use only Sections 1 to n.

Both documents share `preamble.tex`. `exercises.tex` reads the text's labels from `intro.aux`, so `make` builds the
text first. Build both inside Podman with the paper's image:

    podman build -t soup-tex tex
    podman run --rm -v "$PWD/intro:/tex" soup-tex

`checks.py` computes every numeric answer in the solutions (`podman run -i --rm soup python3 - < intro/checks.py`,
output in `checks.out`).
