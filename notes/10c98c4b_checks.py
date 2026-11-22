"""Machine checks behind notes/10c98c4b.md (post hoc; no search, no corpus).

    podman run -i --rm soup python3 - < notes/10c98c4b_checks.py

1. Under B, each absorption law is equivalent to a one-operation law (idempotent translations), by E.
2. The candidate as found (the dossier's six laws) is equivalent to B plus the four translation laws, by E.
3. With x∘y = x·y the laws define rectangular bands, by E.
4. Models of B on 2 and 3 elements are exactly the groupoids orthogonal to their transpose (enumeration of all
   3^9 tables; the decoder ∘ is read off the inverse of (x,y) -> (x·y, y·x)).
5. Which rectangular-band laws hold in the smallest non-degenerate model of the candidate.
"""
import itertools, os, subprocess
import numpy as np

# Self-contained (no import of soup.data, so no matrix or meta file is loaded); copies of soup.named.parse,
# soup.core.is_nondeg and soup.profile.canon.
E_BIN = os.environ.get('SOUP_EPROVER', 'eprover')
PROVER_MB = int(os.environ.get('SOUP_PROVER_MEMORY_MB', 2000))

def parse(s):
    s = s.replace(' ', ''); pos = [0]
    def atom():
        if s[pos[0]] == '(':
            pos[0] += 1; t = expr(); pos[0] += 1; return t
        v = 'xyzwuv'.index(s[pos[0]]); pos[0] += 1; return ('v', v)
    def expr():
        t = atom()
        while pos[0] < len(s) and s[pos[0]] in '·∘':
            op = 'f' if s[pos[0]] == '·' else 'g'; pos[0] += 1
            t = (op, t, atom())
        return t
    return expr()

def essbin(T, n):
    return any(T[x1, y] != T[x2, y] for y in range(n) for x1 in range(n) for x2 in range(n)) and \
           any(T[x, y1] != T[x, y2] for x in range(n) for y1 in range(n) for y2 in range(n))

def is_nondeg(F, G, n):
    return essbin(F, n) and essbin(G, n) and not np.array_equal(F, G)

def canon(n, F, G):
    best = None
    for p in itertools.permutations(range(n)):
        p = np.array(p); q = np.argsort(p)
        k = (p[F[np.ix_(q, q)]].tobytes(), p[G[np.ix_(q, q)]].tobytes())
        if best is None or k < best: best = k
    return best

V = 'XYZWUV'
def tp(t): return V[t[1]] if t[0] == 'v' else f"{t[0]}({tp(t[1])},{tp(t[2])})"
def fof(s, name, role):
    l, r = s.replace(' ', '').split('='); L, R = parse(l), parse(r)
    vs = sorted({c for c in tp(L) + tp(R) if c in V})
    q = f"! [{','.join(vs)}] : " if vs else ''
    return f"fof({name},{role},{q}({tp(L)} = {tp(R)}))."
def E(A, g, cpu=60):
    src = '\n'.join(fof(a, f'a{i}', 'axiom') for i, a in enumerate(A)) + '\n' + fof(g, 'goal', 'conjecture') + '\n'
    o = subprocess.run([E_BIN, '--auto', '-s', f'--cpu-limit={cpu}', f'--memory-limit={PROVER_MB}'],
                       input=src, capture_output=True, text=True).stdout
    st = [l for l in o.splitlines() if 'SZS status' in l]
    return st[-1].split('SZS status')[1].split()[0] if st else 'none'

B = ['(x·y)∘(y·x)=x', '(x∘y)·(y∘x)=x']
ABS = ['(x∘y)·x=x', 'x·(y∘x)=x', '(x·y)∘x=x', 'x∘(y·x)=x']
IT = ['x·(x·y)=x·y', '(x·y)·y=x·y', 'x∘(x∘y)=x∘y', '(x∘y)∘y=x∘y']
FOUND = ['x·(y∘x)=x·x', 'x∘(y·x)=x∘x', '(x∘y)·x=x·x', '(x·y)∘x=x∘x', '(x∘y)·(y∘x)=x', '(x·y)∘(y·x)=x']

print('1. under B, absorption <=> translation law (E, both directions)')
for a, t in zip(ABS, IT):
    print(f'   {a:14s} => {t:14s}: {E(B + [a], t):16s}  <=: {E(B + [t], a)}')

print('2. found laws <=> B + translation laws')
print('   found => each of B+IT:', [E(FOUND, g) for g in B + IT])
print('   B+IT => each found law:', [E(B + IT, g) for g in FOUND])
print('   B+IT => x·x = x:', E(B + IT, 'x·x=x'), ' x∘x = x:', E(B + IT, 'x∘x=x'))
print('   B+IT, three translation laws => the fourth (expect countersatisfiable):',
      [E(B + IT[:i] + IT[i + 1:], IT[i]) for i in range(4)])

print('3. one operation (x∘y := x·y)')
S = sorted({f.replace('∘', '·') for f in FOUND})
RB = ['x·x=x', '(x·y)·z=x·z', 'x·(y·z)=x·z']
print('   S =', S)
print('   S => rectangular band laws:', [E(S, g) for g in RB])
print('   rectangular band => S:', [E(RB, g) for g in S])

print('4. B on small sets: models = groupoids orthogonal to their transpose')
def check_B(F, G, n):
    return all(G[F[x, y], F[y, x]] == x and F[G[x, y], G[y, x]] == x for x in range(n) for y in range(n))
def holds_IT(F, G, n):
    r = range(n)
    return all(F[x, F[x, y]] == F[x, y] and F[F[x, y], y] == F[x, y] and
               G[x, G[x, y]] == G[x, y] and G[G[x, y], y] == G[x, y] for x in r for y in r)
for n in (2, 3):
    orth = 0; iso_all = set(); iso_nd = set(); iso_nd_it = set()
    for vals in itertools.product(range(n), repeat=n * n):
        F = np.array(vals, np.int64).reshape(n, n)
        img = {(F[x, y], F[y, x]): (x, y) for x in range(n) for y in range(n)}
        if len(img) < n * n: continue                       # (x,y) -> (xy, yx) not injective
        orth += 1
        G = np.zeros((n, n), np.int64)
        for (u, v), (x, y) in img.items(): G[u, v] = x
        assert check_B(F, G, n)                             # second coordinate of the inverse is v∘u
        k = canon(n, F, G); iso_all.add(k)
        if is_nondeg(F, G, n):
            iso_nd.add(k)
            if holds_IT(F, G, n): iso_nd_it.add(k)
    print(f'   n={n}: tables orthogonal to their transpose {orth}; B-models up to iso {len(iso_all)}, '
          f'non-degenerate {len(iso_nd)}; non-degenerate with the translation laws {len(iso_nd_it)}')

print('5. smallest non-degenerate model of the candidate (4 elements, dossier)')
F = np.array([[0, 0, 2, 2], [1, 1, 3, 3], [1, 1, 2, 2], [0, 0, 3, 3]])
G = np.array([[0, 0, 3, 3], [1, 1, 2, 2], [0, 0, 2, 2], [1, 1, 3, 3]])
n = 4; r = range(n)
for name, T in (('·', F), ('∘', G)):
    print(f'   {name}: idempotent', all(T[x, x] == x for x in r),
          '| (xy)z = xz', all(T[T[x, y], z] == T[x, z] for x in r for y in r for z in r),
          '| x(yz) = xz', all(T[x, T[y, z]] == T[x, z] for x in r for y in r for z in r),
          '| associative', all(T[T[x, y], z] == T[x, T[y, z]] for x in r for y in r for z in r))
print('   B holds:', check_B(F, G, n), '| translation laws hold:', holds_IT(F, G, n))

print('6. all non-degenerate models of B + translation laws on 4 and 5 elements (Mace4, complete), laws they share')
import re
LADR = """formulas(assumptions).
g(f(x,y),f(y,x)) = x.  f(g(x,y),g(y,x)) = x.
f(x,f(x,y)) = f(x,y).  f(f(x,y),y) = f(x,y).  g(x,g(x,y)) = g(x,y).  g(g(x,y),y) = g(x,y).
end_of_list.
"""
LAWS = {   # name: (law text for E, test on tables T of one operation)
    'x(yz) = xz': ('x·(y·z)=x·z', lambda T, r: all(T[x, T[y, z]] == T[x, z] for x in r for y in r for z in r)),
    '(xy)z = xz': ('(x·y)·z=x·z', lambda T, r: all(T[T[x, y], z] == T[x, z] for x in r for y in r for z in r)),
    'associative': ('(x·y)·z=x·(y·z)', lambda T, r: all(T[T[x, y], z] == T[x, T[y, z]] for x in r for y in r for z in r)),
    'x(yx) = x': ('x·(y·x)=x', lambda T, r: all(T[x, T[y, x]] == x for x in r for y in r)),
    '(xy)x = x': ('(x·y)·x=x', lambda T, r: all(T[T[x, y], x] == x for x in r for y in r)),
    '(xy)(yx) = x': ('(x·y)·(y·x)=x', lambda T, r: all(T[T[x, y], T[y, x]] == x for x in r for y in r)),
}
shared = None
for n in (4, 5):
    out = subprocess.run(['mace4', '-n', str(n), '-N', str(n), '-m', '100000', '-t', '300', '-b', str(PROVER_MB)],
                         input=LADR, capture_output=True, text=True).stdout
    tabs = []
    for blk in out.split('interpretation(')[1:]:
        f = re.search(r'function\(f\(_,_\), \[([\d,\s]+)\]', blk); g = re.search(r'function\(g\(_,_\), \[([\d,\s]+)\]', blk)
        tabs.append((np.array([int(v) for v in f.group(1).replace(' ', '').replace('\n', '').split(',')]).reshape(n, n),
                     np.array([int(v) for v in g.group(1).replace(' ', '').replace('\n', '').split(',')]).reshape(n, n)))
    seen = {}
    for F, G in tabs:
        if is_nondeg(F, G, n): seen.setdefault(canon(n, F, G), (F, G))
    r = range(n)
    tally = {f'{op} {k}': sum(test(T, r) for F, G in seen.values() for T in [F if op == '·' else G])
             for k, (_, test) in LAWS.items() for op in '·∘'}
    done = 'all_models' in out or 'exhausted' in out        # Mace4 ends with "exit (all_models)" when the search is complete
    print(f'   n={n}: {len(tabs)} models found, search complete: {done}; non-degenerate up to iso {len(seen)}')
    print('   laws holding (count of models):', {k: v for k, v in tally.items() if v})
    here = {k for k, v in tally.items() if v == len(seen)}
    shared = here if shared is None else shared & here
    if n in (4, 5):
        # 7. (added 22 Nov, after the literature lookup) is r(x,y) = (x·y, y·x) a set-theoretic YBE solution?
        # braid relation r12 r23 r12 = r23 r12 r23 on triples
        def braid(F):
            r = lambda a, b: (F[a, b], F[b, a])
            ok = True
            for x, y, z in itertools.product(range(n), repeat=3):
                a, b = r(x, y); b, c = r(b, z); a, b = r(a, b); lhs = (a, b, c)
                b, c = r(y, z); a, b = r(x, b); b, c = r(b, c); rhs = (a, b, c)
                if lhs != rhs: ok = False; break
            return ok
        yb = sum(braid(F) for F, G in seen.values())
        print(f'   7. n={n}: r(x,y) = (x·y, y·x) satisfies the braid relation in {yb} of {len(seen)} models')
print('   laws holding in every non-degenerate model on 4 and 5 elements:', sorted(shared))
for k in sorted(shared):
    op, name = k.split(' ', 1); law = LAWS[name][0]
    if op == '∘': law = law.replace('·', '∘')
    print(f'   E: B + translation laws => {law}: {E(B + IT, law)}')
