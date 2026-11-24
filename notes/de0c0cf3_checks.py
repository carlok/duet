"""de0c0cf3 (X7, N1 rank 2), the close look (24 Nov 2026). E 30-60 s per goal; models on TS-quasigroups n <= 4.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/de0c0cf3_checks.py

Part 1: what T implies; a plain reading K (E both ways); T against 3818b88f with ∘ reversed (rev∘ relabelling).
Part 2: models. For every labelled TS-quasigroup on n <= 4 elements, the ∘ satisfying K, those that also satisfy
x∘(x·x) = x (3818b88f's (x·x)∘x = x with ∘ reversed), and a check of sampled models against T's own laws.
"""
import itertools, random, sys
import numpy as np
from soup.core import law_vector
from soup.data import LAWS
from soup.named import law_index
from soup.provers import prove_e
from soup.relabel import _proves, relabel_law


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


T = L(['x·(x·y)=y', '(x·y)∘y=x∘y', '(((x·x)∘x)·y)·y=x'])
K = L(['x·y=y·x', 'x·(x·y)=y', 'x∘x=x', '(x·y)∘y=x∘y'])
C38 = L(['x·(x·y)=y', '(x·y)·y=x', 'x∘(x·y)=x∘y', '(x·x)∘(x∘x)=x', '(x·(x·x))∘x=x'])   # 3818b88f as found
REV_CIRC = (0, 0, 1)                                                                     # reverse ∘ only
C38r = sorted(relabel_law(i, REV_CIRC) for i in C38)
part = sys.argv[1] if len(sys.argv) > 1 else '1'

if part == '1':
    print('T   =', ' & '.join(LAWS[i] for i in T))
    for s in ['x·y=y·x', '(x·y)·y=x', 'x∘x=x', 'x·x=x', 'x·x=y·y', 'x∘y=y∘x', '(x∘y)∘z=x∘(y∘z)', '(x·x)∘x=x',
              'x∘(x·x)=x', 'x∘(x·y)=x∘y', 'x∘y=x', 'x∘y=y', '(x∘y)∘y=x∘y', 'x∘(x∘y)=x∘y', '(x·y)∘x=y∘x']:
        g = law_index(s); r = prove_e(T, g, 500_000, 30)
        print(f'  T => {LAWS[g]:22s} {r["status"]}', flush=True)
    print('K   =', ' & '.join(LAWS[i] for i in K))
    print('  T => K', _proves(T, K, 60), '| K => T', _proves(K, T, 60), flush=True)
    print('3818b88f, rev∘ =', ' & '.join(LAWS[i] for i in C38r))
    print('  3818b88f(rev∘) => T', _proves(C38r, T, 60), flush=True)
    g = law_index('x∘(x·x)=x'); r = prove_e(T, g, 500_000, 60)
    print(f'  T => {LAWS[g]} (3818b88f\'s extra law, rev∘): {r["status"]} ({r["szs"]})', flush=True)


def ts_quasigroups(n):
    """Labelled commutative tables with x·(x·y) = y (totally symmetric quasigroups)."""
    cells = [(i, j) for i in range(n) for j in range(i, n)]
    M = -np.ones((n, n), int)
    def rec(k):
        if k == len(cells):
            if all(M[x, M[x, y]] == y for x in range(n) for y in range(n)): yield M.copy()
            return
        i, j = cells[k]
        for v in range(n):
            if v in M[i] or v in M[:, j] or v in M[j] or v in M[:, i]: continue
            M[i, j] = M[j, i] = v
            yield from rec(k + 1)
            M[i, j] = M[j, i] = -1
    yield from rec(0)


def circ_ops(F, n):
    """All ∘ satisfying K for the TS-quasigroup F: for each y, ∘(-, y) is constant on the orbits {x, x·y} of the
    involution x -> x·y, and y∘y = y."""
    slots = []
    for y in range(n):
        seen = set()
        for x in range(n):
            o = frozenset((x, F[x, y]))
            if o not in seen: seen.add(o); slots.append((y, o))
    for vals in itertools.product(range(n), repeat=len(slots)):
        G = np.zeros((n, n), int)
        for (y, o), v in zip(slots, vals):
            for x in o: G[x, y] = v
        if all(G[x, x] == x for x in range(n)): yield G


def degenerate(G, n):
    return (all(G[x, y] == x for x in range(n) for y in range(n)) or all(G[x, y] == y for x in range(n) for y in range(n))
            or len(set(G.ravel())) == 1)


if part == '2':
    random.seed(0)
    extra = law_index('x∘(x·x)=x')
    for n in range(2, 5):
        tsq = list(ts_quasigroups(n)); tot = nd = with_extra = 0; samples = []; witness = None
        for F in tsq:
            for G in circ_ops(F, n):
                tot += 1
                ok = all(G[x, F[x, x]] == x for x in range(n))
                with_extra += ok
                if not ok and witness is None and not degenerate(G, n): witness = (F, G)
                if degenerate(G, n) or (G == F).all(): continue
                nd += 1
                if len(samples) < 50 or random.random() < 0.01: samples.append((F, G))
        bad = sum(1 for F, G in samples if not law_vector(F, G, n)[T].all())
        print(f'n={n}: {len(tsq)} labelled TS-quasigroups; ∘ satisfying K: {tot} (non-degenerate {nd}); also '
              f'x∘(x·x) = x: {with_extra}; sampled {len(samples)} checked against T: {len(samples) - bad} pass', flush=True)
        if witness:
            F, G = witness; lv = law_vector(F, G, n)
            print(f'  witness: · = {F.tolist()}, ∘ = {G.tolist()}: T holds {bool(lv[T].all())}, '
                  f'x∘(x·x) = x holds {bool(lv[extra])}', flush=True)
