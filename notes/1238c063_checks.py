"""1238c063 (X11, N1 rank 2, unstudied until 27 Nov 2026), the close look; the sibling of 1f430506. E 30-60 s per goal.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/1238c063_checks.py

T2 = {A: (x·y)·(x∘z) = z∘x, C: (x·((x∘y)·x))·y = y}. 1f430506 is T = {A, B: ((x∘y)·(z·z))·x = x}.
V = {A, Q: (x·x)·y = y}, a guess at a common supervariety (notes/1f430506.md, Open).
Part 1: what T2 implies (E), which single law implies what (synergy), the ETP numbers, V against T and T2, and E's
        proof of (x·x)·y = y from T2.
Part 2: the reading. Given ∘ commutative, each law of T2 constrains one value x∘y at a time: x∘y must lie in
        W2(x,y) = {w : p·w = w for every p in x·S and y·S, (x·(w·x))·y = y and (y·(w·y))·x = x}; V drops the last two
        conditions, T replaces them by B's. Checked on every magma with n <= 3: the formula prod_{x<=y} |W(x,y)|
        against Mace4's labelled count, for T2 and V, and the ·-reducts against "(x·x)·y = y and a right zero".
Part 3: n = 4 by the formula, for V, T, T2 and T + T2, over the same ·-reducts.
Part 4: synergy (Mace4 models of each law alone where the emergent laws fail); the goals E left undecided, against the
        models on 2-3 elements; x·y = y with any commutative ∘ is a model of T2.
Part 5: the neighbourhood: every verified theory, in every run, that contains A.
Part 6: a model of V on 2-6 elements where B and C both fail (Mace4, 1,200 s); V with the operations set equal, and V
        with an associative ·.
Part 7: A with the operations identified: its ETP number, and the constant law.
"""
import glob
import itertools
import json
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


A, B, C = L(['(x·y)·(x∘z)=z∘x']), L(['((x∘y)·(z·z))·x=x']), L(['(x·((x∘y)·x))·y=y'])
Q = L(['(x·x)·y=y'])
T = sorted(A + B)                                             # 1f430506
T2 = sorted(A + C)                                            # 1238c063
V = sorted(A + Q)
part = sys.argv[1] if len(sys.argv) > 1 else '1'

GOALS = ['x∘y=y∘x', '(x·x)·y=y', '(x·x)·x=x', '(x∘(x·y))·z=z', '(x∘(y·y))·z=z', '((x·y)∘x)·z=z',
         '(x∘(x·x))·y=y', '((x∘y)·(z·z))·x=x',
         # things the models may rule out (expect unknown or countersatisfiable)
         'x·x=y·y', 'x·x=x', '(x·y)·z=x·(y·z)', 'x·y=y', 'x∘x=x', '(x∘y)∘z=x∘(y∘z)', '(x·(x∘y))·z=z',
         'x·(y·y)=y·y', 'x·(x·y)=y', '(x·(x·x))·y=y', '(x·(x∘x))·y=y']

if part == '1':
    print('T2 =', ' & '.join(LAWS[i] for i in T2))
    for s in GOALS:
        g = law_index(s.replace(' ', '')); r = prove_e(T2, g, 500_000, 30)
        print(f'  T2 => {LAWS[g]:28s} {r["status"]} ({r["szs"]}, {r["proof_steps"]} steps)', flush=True)
    print('Synergy: each law alone')
    for name, S in (('A', A), ('C', C)):
        for s in ['x∘y=y∘x', '(x·x)·y=y', '(x∘(x·x))·y=y']:
            g = law_index(s.replace(' ', '')); r = prove_e(S, g, 500_000, 30)
            print(f'  {name} => {LAWS[g]:24s} {r["status"]} ({r["szs"]})', flush=True)
    from soup.profile import etp_numbers
    for s in ['(x·x)·y=y', '(x·((x·y)·x))·y=y']:
        q = law_index(s)
        print('ETP number of', LAWS[q], '(operations identified):', etp_numbers([q]))
    print('V =', ' & '.join(LAWS[i] for i in V))
    print('  T2 => V', _proves(T2, V, 60), '| T => V', _proves(T, V, 60), flush=True)
    print('  V => C', _proves(V, C, 60), '| V => B', _proves(V, B, 60), flush=True)
    g = law_index('x∘y=y∘x'); r = prove_e(V, g, 500_000, 30)
    print(f'  V => {LAWS[g]} {r["status"]} ({r["szs"]}, {r["proof_steps"]} steps)', flush=True)
    print("E's proof of (x·x)·y = y from T2:")
    src = problem(T2, Q[0])
    r = subprocess.run([E_BIN, '--auto', '--proof-object', '-s', f'--memory-limit={PROVER_MB}', '--cpu-limit=30'],
                       input=src, capture_output=True, text=True, timeout=60)
    for line in r.stdout.splitlines():
        if re.match(r'(c|f)nf\(', line): print('  ' + line[:220])


def fixsets(F, n):
    """For each x: the w fixed by every left translation by an element of x·S (A, given commutativity)."""
    S = range(n)
    P = [{int(F[x, y]) for y in S} for x in S]
    return [{w for w in S if all(F[p, w] == w for p in P[x])} for x in S]


def W(F, n, which):
    """The allowed values of x∘y (x <= y) for V, T (B's condition) or T2 (C's condition)."""
    S = range(n)
    fix = fixsets(F, n)
    U = {int(F[z, z]) for z in S}
    out = {}
    for x in S:
        for y in S:
            if x > y: continue
            ws = fix[x] & fix[y]
            if which == 'T':
                ws = {w for w in ws if all(F[F[w, u], x] == x and F[F[w, u], y] == y for u in U)}
            elif which == 'T2':
                ws = {w for w in ws if F[F[x, F[w, x]], y] == y and F[F[y, F[w, y]], x] == x}
            elif which == 'TT2':
                ws = {w for w in ws if all(F[F[w, u], x] == x and F[F[w, u], y] == y for u in U)
                      and F[F[x, F[w, x]], y] == y and F[F[y, F[w, y]], x] == x}
            out[(x, y)] = ws
    return out


def count(F, n, which): return math.prod(len(s) for s in W(F, n, which).values())
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
        for name, th in (('T2', T2), ('V', V)):
            tot, reducts, bad = 0, 0, 0
            for vals in itertools.product(range(n), repeat=n * n):
                F = np.array(vals, np.int64).reshape(n, n)
                # V has Q as an axiom of ·, on top of the membership conditions
                c = count(F, n, name) if (name != 'V' or has_Q(F, n)) else 0
                tot += c
                if c: reducts += 1
                if (c > 0) != (has_Q(F, n) and has_rz(F, n)): bad += 1
            ms, complete, err = all_models(th, n, cap=50000, secs=300)
            print(f'n={n} {name}: formula {tot} labelled models on {reducts} magmas with a value set everywhere; Mace4 '
                  f'{labelled_count(ms, n)} labelled ({len(ms)} classes, complete={complete}); magmas where '
                  f'"some ∘ exists" and "Q + right zero" disagree: {bad}', flush=True)

if part == '3':
    n = 4
    # magmas with (x·x)·y = y: choose the squares first (each square row is the identity row), then the rest
    nred, tot = 0, {'V': 0, 'T': 0, 'T2': 0, 'TT2': 0}
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
            nred += 1
            for k in tot: tot[k] += count(F, n, k)
    print(f'n=4: {nred} labelled ·-reducts; labelled models by the formula:', tot, flush=True)

if part == '4':
    from soup.core import law_vector
    from soup.profile import all_models
    from soup.provers import mace4
    for name, S in (('A', A), ('C', C)):
        for s in ['x∘y=y∘x', '(x·x)·y=y', '(x∘(x·x))·y=y']:
            g = law_index(s); r = mace4(S, g, 2, 6, 120)
            print(f'  {name} alone, a model where {LAWS[g]} fails: size {r["size"]} {r["tables"]} '
                  f'(searched to {r["searched_to"]}, {r["reason"]})', flush=True)
    ms = [m for n in (2, 3) for m in all_models(T2, n, cap=50000, secs=300)[0]]
    for s in GOALS:
        g = law_index(s.replace(' ', ''))
        bad = next(((n, F, G) for n, F, G in ms if not law_vector(F, G, n)[g]), None)
        print(f'  {LAWS[g]:28s}', 'holds in every model on 2-3 elements' if bad is None else
              f'fails on n={bad[0]}: · {bad[1].tolist()} ∘ {bad[2].tolist()}', flush=True)
    for s in ['(x∘(x·y))·z=z', '((x·y)∘x)·z=z', '((x∘y)·(z·z))·x=x']:
        g = law_index(s); r = mace4(T2, g, 2, 6, 120)
        print(f'  T2, a model where {LAWS[g]} fails: size {r["size"]} {r["tables"]} '
              f'(searched to {r["searched_to"]}, {r["reason"]})', flush=True)
    n = 3; F = np.tile(np.arange(n), (n, 1)); cnt = 0
    for vals in itertools.product(range(n), repeat=6):
        G = np.zeros((n, n), np.int64)
        for (i, j), v in zip([(i, j) for i in range(n) for j in range(i, n)], vals): G[i, j] = G[j, i] = v
        v = law_vector(F, G, n); cnt += bool(v[T2[0]] and v[T2[1]])
    print(f'  x·y = y with a commutative ∘ on 3 elements: {cnt} of 729 are models of T2')

if part == '5':
    a = LAWS[A[0]]
    seen = {}
    for f in sorted(glob.glob('/data/**/results/*.json', recursive=True)):
        try: r = json.load(open(f))
        except Exception: continue
        laws = r.get('laws') or []
        if a not in laws: continue
        k = r.get('key', f.split('/')[-1][:16])
        seen.setdefault(k, (f.split('/data/')[1].split('/results')[0], r.get('score'), laws))
    print(f'verified theories containing {a}: {len(seen)}')
    for k, (run, sc, laws) in sorted(seen.items(), key=lambda kv: -(kv[1][1] or 0)):
        print(f'  {k[:8]} {run:10s} score {sc}  ' + ' & '.join(x for x in laws if x != a))

if part == '6':
    from soup.provers import ladr_input
    # a model of V where B and C both fail (on 4 elements there is none: the part-3 counts give V = T ∪ T2 there)
    neg = ('f(f(g(a1,a2),f(a3,a3)),a1) != a1.\n'          # B fails at (a1, a2, a3)
           'f(f(b1,f(g(b1,b2),b1)),b2) != b2.\n')         # C fails at (b1, b2)
    src = ladr_input(V).replace('end_of_list.\nformulas(goals).', neg + 'end_of_list.\nformulas(goals).', 1)
    r = subprocess.run(['mace4', '-n', '2', '-N', '6', '-t', '1200', '-b', str(PROVER_MB)],
                       input=src, capture_output=True, text=True, timeout=1300)
    m = re.search(r'interpretation\( (\d+),', r.stdout)
    sizes = re.findall(r'DOMAIN SIZE (\d+)', r.stdout)
    print('  V, a model where B and C both fail:', f'size {m.group(1)}' if m else 'none',
          '| sizes started:', sizes, '|', (re.findall(r'Exiting with (.*)\.', r.stdout) or ['?'])[-1], flush=True)
    if m:
        from soup.core import law_vector
        n = int(m.group(1)); tabs = []
        for op in ('f', 'g'):
            t = re.search(op + r'\(_,_\), \[([\d,\s]+)\]', r.stdout)
            tabs.append(np.array([int(v) for v in t.group(1).replace(',', ' ').split()], np.int64).reshape(n, n))
            print(f'    {"·" if op == "f" else "∘"}:', tabs[-1].tolist())
        v = law_vector(tabs[0], tabs[1], n)             # independent re-check on the tables
        print('    re-checked: A', bool(v[A[0]]), 'Q', bool(v[Q[0]]), 'B', bool(v[B[0]]), 'C', bool(v[C[0]]), flush=True)
    Ve = sorted(V + [law_index('x·y=x∘y')])
    r = prove_e(Ve, law_index('x=y'), 500_000, 60); print('  V + x·y = x∘y => x = y:', r['status'], r['szs'])
    Va = sorted(V + [law_index('(x·y)·z=x·(y·z)')])
    r = prove_e(Va, law_index('x·y=y'), 500_000, 60); print('  V + (x·y)·z = x·(y·z) => x·y = y:', r['status'], r['szs'])

if part == '7':
    # A with the operations identified (the literature agent read it as ETP 3772, equivalent to the constant law)
    from soup.profile import etp_numbers
    a = law_index('(x·y)·(x·z)=z·x')
    print(LAWS[a], 'ETP', etp_numbers([a]))
    r = prove_e([a], law_index('x·y=z·w'), 200_000, 20); print('  => x·y = z·w:', r['status'], r['szs'])
