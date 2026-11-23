"""3818b88f: models from totally symmetric quasigroups on n <= 4 elements (23 Nov 2026).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/3818b88f_models.py

Plain reading C (E both ways, notes/x6_top4.md): · commutative with x·(x·y) = y (a TS-quasigroup); ∘ idempotent,
(x·x)∘x = x, x∘(x·y) = x∘y. For each x, the involution y -> x·y splits the set into orbits {y, x·y}; x∘ is constant
on each orbit, x∘x = x (orbit {x, x·x}). So ∘ is free on the other orbits, subject to (x·x)∘x = x.
For every TS-quasigroup on n elements (labelled tables), count the ∘ that satisfy C, the non-degenerate ones (∘ not
a projection or constant, ∘ != ·), and those that are selectors (x∘y in {x, y, x·y}). Then check sampled models
against the theory's original laws with soup's law_vector.
"""
import itertools, random
import numpy as np
from soup.core import law_vector
from soup.named import law_index

T = [law_index(s) for s in ['x·(x·y)=y', '(x·y)·y=x', 'x∘(x·y)=x∘y', '(x·x)∘(x∘x)=x', '(x·(x·x))∘x=x']]


def ts_quasigroups(n):
    cells = [(i, j) for i in range(n) for j in range(i, n)]
    M = -np.ones((n, n), int)
    def ok(i, j, v):
        if v in M[i] or v in M[:, j]: return False
        return True
    def rec(k):
        if k == len(cells):
            # x·(x·y) = y
            if all(M[x, M[x, y]] == y for x in range(n) for y in range(n)): yield M.copy()
            return
        i, j = cells[k]
        for v in range(n):
            if ok(i, j, v) and (i == j or ok(j, i, v)):
                M[i, j] = M[j, i] = v
                yield from rec(k + 1)
                M[i, j] = M[j, i] = -1
    yield from rec(0)


def circ_ops(F, n):
    """All ∘ satisfying C for the TS-quasigroup F (as tables), by choosing a value per (x, orbit)."""
    slots = []                                  # (x, orbit) pairs to choose
    for x in range(n):
        seen = set()
        for y in range(n):
            o = frozenset((y, F[x, y]))
            if o in seen: continue
            seen.add(o); slots.append((x, o))
    for vals in itertools.product(range(n), repeat=len(slots)):
        G = np.zeros((n, n), int)
        for (x, o), v in zip(slots, vals):
            for y in o: G[x, y] = v
        if all(G[x, x] == x for x in range(n)) and all(G[F[x, x], x] == x for x in range(n)):
            yield G


def degenerate(G, n):
    left = all(G[x, y] == x for x in range(n) for y in range(n))
    right = all(G[x, y] == y for x in range(n) for y in range(n))
    const = len(set(G.ravel())) == 1
    return left or right or const


random.seed(0)
for n in range(2, 5):                         # n = 5: about 5^15 choices of ∘ per TS-quasigroup, not enumerated
    tsq = list(ts_quasigroups(n)); tot = nd = sel = 0; samples = []
    for F in tsq:
        for G in circ_ops(F, n):
            tot += 1
            if degenerate(G, n) or (G == F).all(): continue
            nd += 1
            if all(G[x, y] in (x, y, F[x, y]) for x in range(n) for y in range(n)): sel += 1
            if len(samples) < 50 or random.random() < 0.01: samples.append((F, G))
    bad = sum(1 for F, G in samples if not law_vector(F, G, n)[T].all())
    idem = sum(1 for F in tsq if all(F[x, x] == x for x in range(n)))
    print(f'n={n}: {len(tsq)} labelled TS-quasigroups ({idem} idempotent); ∘ satisfying C: {tot}; non-degenerate: {nd}; '
          f'selectors (x∘y in {{x, y, x·y}}): {sel}; sampled {len(samples)} checked against T: {len(samples) - bad} pass',
          flush=True)
