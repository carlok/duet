"""Candidate a9295908 (t4-prior; N1 rank 3): structure (22 Nov 2026, evening).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - [part] < notes/a9295908_checks.py

T = {x·(x∘x) = x, (x∘y)·y = y, x·y = x∘(y·x)}. Parts: 1 associativity of ·; 2 the semilattice characterization;
3 model counts. A proof counts only from E or Vampire; a non-implication only from a finite model or a saturation.
"""
import sys

from soup.data import LAWS
from soup.named import law_index
from soup.provers import prove_e, prove_vampire, mace4


def L(ss): return sorted(law_index(s) for s in ss)


T = L(['x·(x∘x)=x', '(x∘y)·y=y', 'x·y=x∘(y·x)'])
part = sys.argv[1] if len(sys.argv) > 1 else '1'
print('T =', ' & '.join(LAWS[t] for t in T))

if part == '1':
    A = law_index('(x·y)·z=x·(y·z)')
    e = prove_e(T, A, processed_limit=2_000_000, cpu_limit=120, auto='--auto-schedule')
    print('E (auto-schedule, 120 s):', e['status'], {k: e.get(k) for k in ('steps', 'processed') if k in e})
    v = prove_vampire(T, A, cpu_limit=120, extra=('--mode', 'casc'))
    print('Vampire (casc, 120 s):', v['status'])
    m = mace4(T, goal=A, start=2, end=8, seconds=300)
    print('Mace4 countermodel to associativity of ·, sizes 2-8, 300 s: size', m['size'], '| searched to', m['searched_to'],
          '| exhausted to', m['exhausted_to'], f"({m['secs']} s)")
    if m['size']: print('   · =', m['tables'][0], ' ∘ =', m['tables'][1])
    from soup.confluence import check     # E saturates with commutativity unorientable: only ordered rewriting
    c = check(T, A)
    print('saturation certified as a convergent rewrite system:', c.get('ok'), c.get('why', ''))
    for k, v in c.items():
        if k not in ('ok', 'why'): print('  ', k, ':', v if not isinstance(v, list) else '\n     '.join(map(str, v)))

# C: a commutative idempotent groupoid (·) with x∘(x·y) = x·y and (x∘y)·y = y. Conjecture: T and C are equivalent.
C = L(['x·x=x', 'x·y=y·x', 'x∘(x·y)=x·y', '(x∘y)·y=y'])
CS = C + L(['(x·y)·z=x·(y·z)'])                       # the semilattice case

if part == '2':
    print('C =', ' & '.join(LAWS[t] for t in C))
    for name, A, B in (('T => C', T, C), ('C => T', C, T)):
        res = {LAWS[b]: prove_e(A, b, processed_limit=500_000, cpu_limit=60)['status'] for b in B if b not in A}
        print(name, res)
    # extra consequences
    for g in ['x∘x=x', 'x·(x∘y)=x·y', 'x∘(y∘x)=x', 'x∘(x∘y)=x∘y', '(x∘y)∘y=x∘y', 'x∘y=y']:
        print(f'  T => {LAWS[law_index(g)]:22s}', prove_e(T, law_index(g), processed_limit=500_000, cpu_limit=30)['status'])

if part == '3':
    import numpy as np
    from soup.core import law_vector, is_nondeg
    from soup.profile import all_models
    A = law_index('(x·y)·z=x·(y·z)')
    for n in range(2, 6):
        r = all_models(T, n, 20000, 300)
        ms, complete = r[0], r[1] if len(r) > 1 else None
        rp = sum(1 for _, F, G in ms if all(G[x][y] == y for x in range(n) for y in range(n)))
        assoc = sum(1 for _, F, G in ms if law_vector(np.asarray(F), np.asarray(G), n)[A])
        nd = sum(1 for _, F, G in ms if is_nondeg(F, G, n))
        print(f'n = {n}: {len(ms)} models up to iso (complete {complete}); · associative in {assoc}; '
              f'∘ the right projection in {rp}; non-degenerate {nd}')

if part == '4':
    # the threshold model x∘y = (y if y ≤ x else top) with · the meet, on Boolean algebras (subsets of k points):
    # Lean proves it for every meet-semilattice with a top (lean/Duet/A9295908.lean, threshold_model)
    import numpy as np
    from soup.core import law_vector, is_nondeg
    for k in (2, 3):
        n = 2 ** k; top = n - 1
        meet = np.array([[x & y for y in range(n)] for x in range(n)])
        thr = np.array([[y if (y & x) == y else top for y in range(n)] for x in range(n)])
        lv = law_vector(meet, thr, n)
        print(f'Boolean algebra 2^{k}: threshold model {all(lv[t] for t in T)}, non-degenerate {is_nondeg(meet, thr, n)}')

if part == '5':
    # independent count: commutative idempotent groupoids on 3 elements up to isomorphism (part 3 found 7 models of T
    # with ∘ the right projection; the characterization says they correspond one to one)
    import itertools
    n, seen = 3, set()
    for vals in itertools.product(range(n), repeat=3):
        t = {(i, i): i for i in range(n)}
        for (a, b), v in zip([(0, 1), (0, 2), (1, 2)], vals): t[(a, b)] = t[(b, a)] = v
        key = min(tuple(p[t[(p.index(x), p.index(y))]] for x in range(n) for y in range(n))
                  for p in itertools.permutations(range(n)))
        seen.add(key)
    print('commutative idempotent groupoids on 3 elements up to isomorphism:', len(seen))
