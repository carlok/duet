"""1f430506 (X11, N1 rank 1, unstudied until 27 Nov 2026), the close look. E 20-60 s per goal.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/1f430506_checks.py

T = {A: (x·y)·(x∘z) = z∘x, B: ((x∘y)·(z·z))·x = x}.
Part 1: what T implies (E), which single law implies what (synergy), E's proof of (x·x)·y = y, the ETP number, and
        T against 1238c063 (N1 rank 2, shares A).
Part 2: the reading. Given ∘ commutative, A and B constrain each value x∘y on its own: x∘y must lie in
        W(x,y) = {w : p·w = w for every p in x·S and y·S, and (w·u)·x = x, (w·u)·y = y for every square u}.
        So a model is a magma plus a commutative choice x∘y in W(x,y). Checked on every magma with n <= 3: the formula
        prod_{x<=y} |W(x,y)| against Mace4's models (labelled count from the isomorphism classes), and the claim that
        the ·-reducts are exactly the magmas with (x·x)·y = y and a right zero (an r with x·r = r for all x).
Part 3: n = 4 by the formula: the ·-reducts (magmas with (x·x)·y = y and a right zero, enumerated square map first)
        and their number of ∘, labelled.
Part 4: synergy (Mace4 models of A alone where the emergent laws fail); the goals E left undecided, against the models
        on 2-3 elements; every magma with (x·x)·y = y (n <= 3) becomes a ·-reduct once a right zero and left identity is
        adjoined; x·y = y with any commutative ∘ is a model.
Part 5: Mace4 models of B alone where the emergent laws fail, and a 4-element model of T where (x·(x∘y))·z = z fails.
Part 6: T against 1238c063: a model of each where the other fails, and what 1238c063 proves.
Part 7: the operations set equal; an associative ·.
"""
import itertools
import math
import re
import subprocess
import sys

import numpy as np

from soup.data import LAWS
from soup.named import law_index
from soup.provers import prove_e, problem, E_BIN, PROVER_MB
from soup.relabel import _proves


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


A, B = L(['(x·y)·(x∘z)=z∘x']), L(['((x∘y)·(z·z))·x=x'])
T = sorted(A + B)
T2 = L(['(x·y)·(x∘z)=z∘x', '(x·((x∘y)·x))·y=y'])          # 1238c063
part = sys.argv[1] if len(sys.argv) > 1 else '1'

GOALS = ['x∘y=y∘x', '(x·x)·y=y', '(x·x)·x=x', '(x∘(x·y))·z=z', '(x∘(y·y))·z=z', '((x·y)∘x)·z=z',
         # things the models rule out, for the record (expect unknown or countersatisfiable)
         'x·x=y·y', 'x·x=x', '(x·y)·z=x·(y·z)', 'x·y=y', 'x∘x=x', '(x∘y)∘z=x∘(y∘z)', '(x·(x∘y))·z=z',
         'x·(y·y)=y·y', 'x·(x·y)=y']

if part == '1':
    print('T =', ' & '.join(LAWS[i] for i in T))
    for s in GOALS:
        g = law_index(s.replace(' ', '')); r = prove_e(T, g, 500_000, 30)
        print(f'  T => {LAWS[g]:26s} {r["status"]} ({r["szs"]}, {r["proof_steps"]} steps)', flush=True)
    print('Synergy: each law alone')
    for name, S in (('A', A), ('B', B)):
        for s in ['x∘y=y∘x', '(x·x)·y=y', '(x∘(x·x))·y=y']:
            g = law_index(s.replace(' ', '')); r = prove_e(S, g, 500_000, 30)
            print(f'  {name} => {LAWS[g]:24s} {r["status"]} ({r["szs"]})', flush=True)
    from soup.profile import etp_numbers
    q = law_index('(x·x)·y=y')
    print('ETP number of', LAWS[q], '(operations identified):', etp_numbers([q]))
    print('T2 (1238c063) =', ' & '.join(LAWS[i] for i in T2))
    print('  T => T2', _proves(T, T2, 60), '| T2 => T', _proves(T2, T, 60), flush=True)
    print("E's proof of (x·x)·y = y:")
    src = problem(T, q)
    r = subprocess.run([E_BIN, '--auto', '--proof-object', '-s', f'--memory-limit={PROVER_MB}', '--cpu-limit=30'],
                       input=src, capture_output=True, text=True, timeout=60)
    for line in r.stdout.splitlines():
        if re.match(r'(c|f)nf\(', line): print('  ' + line[:220])


def W(F, n):
    """W(x,y) for the magma F, as a dict of sets; the squares are taken as the u of B."""
    S = range(n)
    U = {int(F[z, z]) for z in S}
    P = [{int(F[x, y]) for y in S} for x in S]
    fix = [{w for w in S if all(F[p, w] == w for p in P[x])} for x in S]
    ok = [{w for w in S if all(F[F[w, u], x] == x for u in U)} for x in S]
    return {(x, y): fix[x] & fix[y] & ok[x] & ok[y] for x in S for y in S if x <= y}


def has_Q(F, n): return all(F[F[x, x], y] == y for x in range(n) for y in range(n))
def has_rz(F, n): return any(all(F[y, w] == w for y in range(n)) for w in range(n))


def labelled_count(models, n):
    """Labelled models from isomorphism classes: sum of n! / |Aut|."""
    tot = 0
    for _, F, G in models:
        aut = sum(1 for p in itertools.permutations(range(n))
                  if all(p[F[a, b]] == F[p[a], p[b]] and p[G[a, b]] == G[p[a], p[b]] for a in range(n) for b in range(n)))
        tot += math.factorial(n) // aut
    return tot


if part == '2':
    from soup.profile import all_models
    for n in (2, 3):
        tot, reducts, bad = 0, 0, 0
        for vals in itertools.product(range(n), repeat=n * n):
            F = np.array(vals, np.int64).reshape(n, n)
            Wd = W(F, n)
            c = math.prod(len(s) for s in Wd.values())
            tot += c
            if c: reducts += 1
            if (c > 0) != (has_Q(F, n) and has_rz(F, n)): bad += 1
        ms, complete, err = all_models(T, n, cap=20000, secs=120)
        print(f'n={n}: formula {tot} labelled models on {reducts} ·-reducts; Mace4 {labelled_count(ms, n)} labelled '
              f'({len(ms)} classes, complete={complete}); magmas where "reduct" and "Q + right zero" disagree: {bad}',
              flush=True)

if part == '3':
    n = 4
    # magmas with (x·x)·y = y: choose the squares first (each square row is the identity row), then the rest
    count_reducts, count_models = 0, 0
    for sq in itertools.product(range(n), repeat=n):
        U = set(sq)
        if any(sq[u] != u for u in U): continue                  # a square u is a left identity, so u·u = u
        free = [(x, y) for x in range(n) for y in range(n) if x not in U and x != y]
        for vals in itertools.product(range(n), repeat=len(free)):
            F = np.zeros((n, n), np.int64)
            for x in range(n):
                F[x, x] = sq[x]
                if x in U: F[x] = np.arange(n)
            for (x, y), v in zip(free, vals): F[x, y] = v
            if not (has_Q(F, n) and has_rz(F, n)): continue
            c = math.prod(len(s) for s in W(F, n).values())
            count_reducts += 1; count_models += c
    print(f'n=4: {count_reducts} labelled ·-reducts, {count_models} labelled models by the formula', flush=True)

if part == '4':
    from soup.core import law_vector
    from soup.profile import all_models
    from soup.provers import mace4
    # synergy: A alone (E was undecided), finite countermodels
    for s in ['x∘y=y∘x', '(x·x)·y=y', '(x∘(x·x))·y=y']:
        g = law_index(s); r = mace4(A, g, 2, 6, 120)
        print(f'  A alone, a model where {LAWS[g]} fails: size {r["size"]} {r["tables"]} '
              f'(searched to {r["searched_to"]}, {r["reason"]})', flush=True)
    # the goals E left undecided, refuted by the smallest model of T where they fail
    ms = [m for n in (2, 3) for m in all_models(T, n, cap=20000, secs=120)[0]]
    for s in GOALS:
        g = law_index(s.replace(' ', ''))
        bad = next(((n, F, G) for n, F, G in ms if not law_vector(F, G, n)[g]), None)
        print(f'  {LAWS[g]:26s}', 'holds in every model on 2-3 elements' if bad is None else
              f'fails on n={bad[0]}: · {bad[1].tolist()} ∘ {bad[2].tolist()}', flush=True)
    # every magma with (x·x)·y = y embeds in a ·-reduct: adjoin r with x·r = r and r·y = y
    for n in (2, 3):
        qm = ok = 0
        for vals in itertools.product(range(n), repeat=n * n):
            F = np.array(vals, np.int64).reshape(n, n)
            if not has_Q(F, n): continue
            qm += 1
            F2 = np.zeros((n + 1, n + 1), np.int64); F2[:n, :n] = F; F2[:, n] = n; F2[n, :] = np.arange(n + 1)
            ok += has_Q(F2, n + 1) and has_rz(F2, n + 1) and math.prod(len(s) for s in W(F2, n + 1).values()) > 0
        print(f'  n={n}: {qm} magmas with (x·x)·y = y; {ok} of them become ·-reducts with a right zero adjoined')
    # ∘ is free: x·y = y with any commutative ∘ is a model (n = 3, all 729)
    n = 3; F = np.tile(np.arange(n), (n, 1)); cnt = 0
    for vals in itertools.product(range(n), repeat=6):
        G = np.zeros((n, n), np.int64)
        for (i, j), v in zip([(i, j) for i in range(n) for j in range(i, n)], vals): G[i, j] = G[j, i] = v
        v = law_vector(F, G, n); cnt += bool(v[T[0]] and v[T[1]])
    print(f'  x·y = y with a commutative ∘ on 3 elements: {cnt} of 729 are models')

if part == '5':
    from soup.provers import mace4
    for name, S, s in (('B', B, 'x∘y=y∘x'), ('B', B, '(x·x)·y=y'), ('T', T, '(x·(x∘y))·z=z')):
        g = law_index(s); r = mace4(S, g, 2, 6, 120)
        print(f'  {name}, a model where {LAWS[g]} fails: size {r["size"]} {r["tables"]} '
              f'(searched to {r["searched_to"]}, {r["reason"]})', flush=True)

if part == '6':
    from soup.provers import mace4
    # T against 1238c063 (T2): a model of each where the other's second law fails
    for name, S, g in (('T', T, [i for i in T2 if i not in T][0]), ('T2', T2, B[0])):
        r = mace4(S, g, 2, 6, 120)
        print(f'  {name}, a model where {LAWS[g]} fails: size {r["size"]} {r["tables"]} '
              f'(searched to {r["searched_to"]}, {r["reason"]})', flush=True)
    for s in ['x∘y=y∘x', '(x·x)·y=y']:
        g = law_index(s); r = prove_e(T2, g, 500_000, 30)
        print(f'  T2 => {LAWS[g]:20s} {r["status"]} ({r["szs"]})', flush=True)

if part == '7':
    # the operations set equal: x·y = x∘y
    from soup.provers import mace4
    from soup.profile import all_models
    Te = sorted(T + [law_index('x·y=x∘y')])
    r = prove_e(Te, law_index('x=y'), 500_000, 60); print('  T + x·y = x∘y => x = y:', r['status'], r['szs'])
    for n in (2, 3, 4, 5):
        ms, complete, err = all_models(Te, n, cap=2000, secs=120)
        print(f'  n={n}: {len(ms)} models up to isomorphism (complete={complete})', [m[1].tolist() for m in ms[:4]],
              flush=True)
    # an associative ·: x·y = (x·r)·y = r·y = y for a right zero r
    Ta = sorted(T + [law_index('(x·y)·z=x·(y·z)')])
    r = prove_e(Ta, law_index('x·y=y'), 500_000, 60); print('  T + (x·y)·z = x·(y·z) => x·y = y:', r['status'], r['szs'])
