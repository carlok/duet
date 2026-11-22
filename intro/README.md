An introduction to the project from scratch: sets and functions, binary operations, laws, theories and models,
synergy, and how the search works, with exercises and solutions. Build inside Podman with the paper's image:

    podman build -t soup-tex tex
    podman run --rm -v "$PWD/intro:/tex" soup-tex

`checks.py` computes every numeric answer in the solutions (`podman run -i --rm soup python3 - < intro/checks.py`,
output in `checks.out`).
