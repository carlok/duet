"""71fd2cc6 (X12 fusion6, N1 rank 18, top score of X12), the close look (27 Nov 2026). E 30-60 s per goal.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <part> < notes/71fd2cc6_checks.py

T = {x·y = y·x, x∘(x·y) = y∘x, (x∘y)·z = y·(z·x)}.
Part 1: what T implies, and a plain reading K (E both ways).
Part 2: models. Every labelled commutative semigroup on n <= 4 elements (n = 5 with --five), and for each, every ∘ with
K's laws; counted against T's own laws, with the non-degenerate ones (∘ ≠ ·, both essentially binary) apart.
"""
import itertools
import sys

import numpy as np

from soup.data import LAWS
from soup.named import law_index
from soup.provers import prove_e
from soup.relabel import _proves


def L(ss): return sorted(law_index(s.replace(' ', '')) for s in ss)


T = L(['x·y=y·x', 'x∘(x·y)=y∘x', '(x∘y)·z=y·(z·x)'])
K = L(['x·y=y·x', '(x·y)·z=x·(y·z)', 'x∘y=y∘x', '(x∘y)·z=(x·y)·z', 'x∘(x·y)=x∘y'])
part = sys.argv[1] if len(sys.argv) > 1 else '1'

if part == '1':
    print('T =', ' & '.join(LAWS[i] for i in T))
    for s in ['x∘y=y∘x', '(x·y)·z=x·(y·z)', 'x·(y·z)=y·(x·z)', '(x∘y)·z=(x·y)·z', 'x∘(x·y)=x∘y',
              'x·(x·y)=x·(y·y)', '(x∘y)∘z=x∘(y∘z)', 'x∘(x∘y)=x∘y', 'x∘x=x·x', 'x∘y=x·y', 'x·x=x', 'x∘x=x',
              'x·(x·x)=x·x', 'x·x=y·y', 'x∘(y∘z)=x∘(y·z)', '(x∘y)∘z=(x·y)∘z', 'x∘(y·z)=(x∘y)·z',
              'x∘(y·z)=x·(y∘z)', '(x∘y)∘z=(x·y)·z', 'x∘(x∘x)=x∘x', '(x∘x)∘x=x·(x·x)']:
        g = law_index(s.replace(' ', '')); r = prove_e(T, g, 500_000, 30)
        print(f'  T => {LAWS[g]:24s} {r["status"]} ({r.get("szs")})', flush=True)
    print('K =', ' & '.join(LAWS[i] for i in K))
    print('  T => K', _proves(T, K, 60), '| K => T', _proves(K, T, 60), flush=True)
    # a symmetric reading: two commutative semigroups, each blind to the other one level down, ∘ with x∘x∘y = x∘y
    K3 = L(['x·y=y·x', '(x·y)·z=x·(y·z)', 'x∘y=y∘x', '(x∘y)∘z=x∘(y∘z)', 'x·(y∘z)=x·(y·z)', 'x∘(y·z)=x∘(y∘z)',
            'x∘(x∘y)=x∘y'])
    print('K3 =', ' & '.join(LAWS[i] for i in K3))
    print('  T => K3', _proves(T, K3, 60), '| K3 => T', _proves(K3, T, 60), flush=True)
    # is x∘(x∘y) = x∘y needed? the two semigroups and the two blind laws alone
    K4 = L(['x·y=y·x', '(x·y)·z=x·(y·z)', 'x∘y=y∘x', '(x∘y)∘z=x∘(y∘z)', 'x·(y∘z)=x·(y·z)', 'x∘(y·z)=x∘(y∘z)'])
    for s in ['x∘(x∘y)=x∘y', 'x·(x·y)=x·(y·y)', 'x∘(x·y)=y∘x']:
        g = law_index(s); r = prove_e(K4, g, 500_000, 30)
        print(f'  K4 (K3 without x∘(x∘y)=x∘y) => {LAWS[g]:20s} {r["status"]} ({r.get("szs")})', flush=True)
    # Loday's dimonoid axiom D3 with ⊣ = ·, ⊢ = ∘ (D1, D2, D4, D5 hold in T, either way round)
    for s in ['(x∘y)·z=x∘(y·z)', '(x·y)∘z=x·(y∘z)', '(x·y)·z=(x∘y)∘z']:
        g = law_index(s); r = prove_e(T, g, 500_000, 60)
        print(f'  T => {LAWS[g]:22s} (dimonoid D3) {r["status"]} ({r.get("szs")})', flush=True)


def comm_semigroups(n):
    """Labelled commutative semigroups on {0..n-1}, by backtracking over the upper triangle with an associativity check
    on every triple whose products are all filled in."""
    cells = [(i, j) for i in range(n) for j in range(i, n)]
    M = -np.ones((n, n), int)

    def ok():
        for a in range(n):
            for b in range(n):
                ab = M[a, b]
                if ab < 0: continue
                for c in range(n):
                    bc = M[b, c]
                    if bc < 0: continue
                    l, r = M[ab, c], M[a, bc]
                    if l >= 0 and r >= 0 and l != r: return False
        return True

    def rec(k):
        if k == len(cells):
            yield M.copy(); return
        i, j = cells[k]
        for v in range(n):
            M[i, j] = M[j, i] = v
            if ok(): yield from rec(k + 1)
            M[i, j] = M[j, i] = -1
    yield from rec(0)


def essentially_binary(G, n):
    dep_x = any(G[a, y] != G[b, y] for a in range(n) for b in range(n) for y in range(n))
    dep_y = any(G[x, a] != G[x, b] for a in range(n) for b in range(n) for x in range(n))
    return dep_x and dep_y


def circ_ops(F, n):
    """Every commutative ∘ with (x∘y)·z = (x·y)·z and x∘(x·y) = x∘y on the commutative semigroup F."""
    sig = [tuple(F[a]) for a in range(n)]                      # a's translation z -> a·z
    cls = [[b for b in range(n) if sig[b] == sig[F[x, y]]] for x in range(n) for y in range(n)]
    pairs = [(x, y) for x in range(n) for y in range(x, n)]
    G = -np.ones((n, n), int)

    def rec(k):
        if k == len(pairs):
            if all(G[x, F[x, y]] == G[x, y] for x in range(n) for y in range(n)): yield G.copy()
            return
        x, y = pairs[k]
        for v in cls[x * n + y]:
            G[x, y] = G[y, x] = v
            if all(G[a, F[a, b]] < 0 or G[a, b] < 0 or G[a, F[a, b]] == G[a, b] for a in range(n) for b in range(n)):
                yield from rec(k + 1)
            G[x, y] = G[y, x] = -1
    yield from rec(0)


def holds_T(F, G, n):
    R = range(n)
    return (all(F[x, y] == F[y, x] for x in R for y in R)
            and all(G[x, F[x, y]] == G[y, x] for x in R for y in R)
            and all(F[G[x, y], z] == F[y, F[z, x]] for x in R for y in R for z in R))


if part == '2':
    sizes = (2, 3, 4, 5) if '--five' in sys.argv else (2, 3, 4)
    for n in sizes:
        nS = nS_ok = total = nondeg = 0; examples = []; stats = {'D3 fails': 0, '∘ idempotent': 0,
                                                                  'x·x = x∘x everywhere': 0, '∘ = ·': 0}
        R = range(n)
        for F in comm_semigroups(n):
            nS += 1
            got = False
            for G in circ_ops(F, n):
                assert holds_T(F, G, n)
                total += 1; got = True
                if not np.array_equal(F, G) and essentially_binary(F, n) and essentially_binary(G, n):
                    nondeg += 1
                    if len(examples) < 3: examples.append((F.copy(), G.copy()))
                    stats['D3 fails'] += any(F[F[x, y], z] != G[G[x, y], z] for x in R for y in R for z in R)
                    stats['∘ idempotent'] += all(G[x, x] == x for x in R)
                    stats['x·x = x∘x everywhere'] += all(G[x, x] == F[x, x] for x in R)
                stats['∘ = ·'] += np.array_equal(F, G)
            nS_ok += got
        print(f'n = {n}: commutative semigroups {nS}, with some ∘ {nS_ok}; models of T {total}, non-degenerate '
              f'{nondeg}; among the non-degenerate: {({k: v for k, v in stats.items() if k != "∘ = ·"})}; '
              f'∘ = · in {stats["∘ = ·"]}', flush=True)
        for F, G in examples:
            print('  ·', F.tolist(), ' ∘', G.tolist())


if part == '3':
    # The twin reading. rho: a rho b iff a·z = b·z for all z (equal translations). Is x∘y a function of the rho-class of
    # x·y (a choice of one element per class)? And is every such choice a model, whenever one is?
    from soup.provers import mace4
    for n in (2, 3, 4):
        models = fn_of_class = semigroups = all_choices_ok = some_choice_ok = 0
        for F in comm_semigroups(n):
            R = range(n)
            sig = [tuple(F[a]) for a in R]
            classes = {}
            for a in R: classes.setdefault(sig[a], []).append(a)
            prods = sorted({sig[F[x, y]] for x in R for y in R})            # classes that contain a product
            Gs = list(circ_ops(F, n))
            for G in Gs:
                models += 1
                fn_of_class += all(G[x, y] == G[u, v] for x in R for y in R for u in R for v in R
                                   if sig[F[x, y]] == sig[F[u, v]])
            # every choice tau of one element per product class: x∘y = tau(class of x·y)
            choices = list(itertools.product(*[classes[c] for c in prods]))
            ok = 0
            for ch in choices:
                tau = dict(zip(prods, ch))
                G = np.array([[tau[sig[F[x, y]]] for y in R] for x in R])
                ok += holds_T(F, G, n)
            semigroups += 1
            all_choices_ok += ok == len(choices)
            some_choice_ok += ok > 0
        print(f'n = {n}: models {models}, x∘y a function of the class of x·y in {fn_of_class}; commutative semigroups '
              f'{semigroups}: every choice of twins a model in {all_choices_ok}, some choice in {some_choice_ok}',
              flush=True)
    K4 = L(['x·y=y·x', '(x·y)·z=x·(y·z)', 'x∘y=y∘x', '(x∘y)∘z=x∘(y∘z)', 'x·(y∘z)=x·(y·z)', 'x∘(y·z)=x∘(y∘z)'])
    for s in ['x∘(x∘y)=x∘y', 'x·(x·y)=x·(y·y)']:
        m = mace4(K4, law_index(s), 2, 8, 300)
        print(f'K4 without {s}: Mace4 countermodel size {m["size"]} ({m["reason"]}, {m["secs"]} s)', flush=True)
        if m['tables']: print('  ·', m['tables'][0], ' ∘', m['tables'][1])
    # which semigroup laws does T force on (S,·) alone? x·(x·y) = x·(y·y) is proved; is x·(x·y) = x·y?
    for s in ['x·(x·y)=x·y', 'x·(x·x)=x·x', 'x·(y·(x·y))=x·y']:
        m = mace4(T, law_index(s), 2, 8, 120)
        print(f'T and not {s}: Mace4 model size {m["size"]} ({m["reason"]}, {m["secs"]} s)', flush=True)
        if m['tables']: print('  ·', m['tables'][0], ' ∘', m['tables'][1])


if part == '4':
    # the two lemmas of the hand proof (notes/71fd2cc6.md): ∘ is a function of ·, x∘y = (x·y)∘(x·y), and ∘ cannot
    # tell rho-equivalent elements apart, x∘y = (x·y)∘y; and the ∘-products are ∘-idempotent
    for s in ['x∘y=(x·y)∘(x·y)', 'x∘y=(x·y)∘y', '(x∘y)∘(x∘y)=x∘y', 'x∘(x∘(y∘y))=x∘y']:
        g = law_index(s); r = prove_e(T, g, 500_000, 60)
        print(f'  T => {LAWS[g]:24s} {r["status"]} ({r.get("szs")}, steps {r.get("steps")})', flush=True)


if part == '5':
    # is associativity of · (and of ∘) emergent: implied by T, by no single law of T?
    for goal in ['(x·y)·z=x·(y·z)', '(x∘y)∘z=x∘(y∘z)']:
        g = law_index(goal)
        for t in T:
            r = prove_e([t], g, 200_000, 30)
            print(f'  {LAWS[t]:24s} => {LAWS[g]:22s} {r["status"]} ({r.get("szs")})', flush=True)


if part == '6':
    # commutative g-dimonoids (Movsisyan, Davidov, Safaryan 2014; Zhuchok and Zhuchok 2015): Loday's dimonoid axioms
    # D1, D2, D4, D5 without D3, both operations commutative; here with ⊣ = · and ⊢ = ∘
    CG = L(['x·y=y·x', 'x∘y=y∘x',
            '(x·y)·z=x·(y·z)',          # D1
            '(x·y)·z=x·(y∘z)',          # D2: (x⊣y)⊣z = x⊣(y⊢z)
            '(x·y)∘z=x∘(y∘z)',          # D4: (x⊣y)⊢z = x⊢(y⊢z)
            '(x∘y)∘z=x∘(y∘z)'])         # D5
    E1 = L(['x∘(x∘y)=x∘y'])
    print('CG =', ' & '.join(LAWS[i] for i in CG))
    print('  T => CG', _proves(T, CG, 60), flush=True)
    print('  CG + x∘(x∘y)=x∘y => T', _proves(sorted(set(CG) | set(E1)), T, 60), flush=True)
    r = prove_e(CG, law_index('x∘(x∘y)=x∘y'), 500_000, 60)
    print(f'  CG => x∘(x∘y)=x∘y: {r["status"]} ({r.get("szs")})', flush=True)
    # and with the roles swapped (⊣ = ∘, ⊢ = ·)
    CG2 = L(['x·y=y·x', 'x∘y=y∘x', '(x∘y)∘z=x∘(y∘z)', '(x∘y)∘z=x∘(y·z)', '(x∘y)·z=x·(y·z)', '(x·y)·z=x·(y·z)'])
    print('  T => CG (roles swapped)', _proves(T, CG2, 60), '| CG (swapped) == CG:', _proves(CG2, CG, 60) and _proves(CG, CG2, 60), flush=True)
