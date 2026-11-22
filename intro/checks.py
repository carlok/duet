"""Machine checks for the exercises of intro.tex: every numeric answer in the solutions is printed here.

    podman run -i --rm soup python3 - < intro/checks.py

Plain Python, brute force on small tables; no project data is loaded.
"""
import itertools

# a binary operation on {0, ..., n-1} is a tuple of n*n entries: op[x*n + y] = x . y


def ops(n):
    return itertools.product(range(n), repeat=n * n)


def f(op, n):
    return lambda x, y: op[x * n + y]


def holds(law, n, k):
    """law: a function of k elements returning (left, right)."""
    return all(l == r for l, r in (law(*v) for v in itertools.product(range(n), repeat=k)))


print('Ex. 2.1  operations on 2 elements:', sum(1 for _ in ops(2)), '| on 3 elements:', sum(1 for _ in ops(3)))

mx = lambda x, y: max(x, y)
laws = {
    'associative (x.y).z = x.(y.z)': (lambda a, b, c: (mx(mx(a, b), c), mx(a, mx(b, c))), 3),
    'commutative x.y = y.x': (lambda a, b: (mx(a, b), mx(b, a)), 2),
    'idempotent x.x = x': (lambda a: (mx(a, a), a), 1),
    'left projection x.y = x': (lambda a, b: (mx(a, b), a), 2),
    'x.(x.y) = x.y': (lambda a, b: (mx(a, mx(a, b)), mx(a, b)), 2),
}
print('Ex. 3.1  max on {0,1,2}:', {k: holds(l, 3, ar) for k, (l, ar) in laws.items()},
      '| 0 is an identity:', all(mx(0, x) == x for x in range(3)))

lp = lambda x, y: x
print('Ex. 3.2  left projection on {0,1}: associative', holds(lambda a, b, c: (lp(lp(a, b), c), lp(a, lp(b, c))), 2, 3),
      'idempotent', holds(lambda a: (lp(a, a), a), 2, 1), 'commutative', holds(lambda a, b: (lp(a, b), lp(b, a)), 2, 2))
print('Ex. 3.3  checks needed for associativity on 3 elements: 3^3 =', 3 ** 3, '| on 6 elements:', 6 ** 3)

# Ex. 4.x: the absorption pair and its parts on 2 elements
n = 2
both = one_only = 0
m1_not_idem = None
for F in ops(n):
    for G in ops(n):
        a, b = f(F, n), f(G, n)
        l1 = holds(lambda x, y: (a(x, b(x, y)), x), n, 2)
        l2 = holds(lambda x, y: (b(x, a(x, y)), x), n, 2)
        if l1 and l2:
            both += 1
        if l1 and not holds(lambda x: (a(x, x), x), n, 1) and m1_not_idem is None:
            m1_not_idem = (F, G)
print('Ex. 4.2  pairs (., o) on {0,1} satisfying both absorption laws:', both)
NAMES = {(0, 0, 1, 1): 'left projection', (0, 1, 0, 1): 'right projection', (0, 1, 1, 1): 'max', (0, 0, 0, 1): 'min'}
pairs = [(NAMES.get(F, F), NAMES.get(G, G)) for F in ops(2) for G in ops(2)
         if holds(lambda x, y: (f(F, 2)(x, f(G, 2)(x, y)), x), 2, 2) and holds(lambda x, y: (f(G, 2)(x, f(F, 2)(x, y)), x), 2, 2)]
print('         they are:', pairs)
print('Ex. 4.3  a model of x.(x o y) = x alone in which x.x = x fails: . =', m1_not_idem[0], 'o =', m1_not_idem[1])

# Ex. 4.4: a cheap corpus guess that is wrong
corpus = {'2-element lattice max': (0, 1, 1, 1), 'left projection': (0, 0, 1, 1)}
assoc = lambda op, n: holds(lambda x, y, z: (f(op, n)(f(op, n)(x, y), z), f(op, n)(x, f(op, n)(y, z))), n, 3)
print('Ex. 4.4  in the corpus every idempotent table is associative:',
      all(assoc(op, 2) for op in corpus.values() if holds(lambda x: (f(op, 2)(x, x), x), 2, 1)))
st = tuple((2 * x + 2 * y) % 3 for x in range(3) for y in range(3))
print('         x.y = 2x+2y mod 3: idempotent', holds(lambda x: (f(st, 3)(x, x), x), 3, 1), '| associative', assoc(st, 3),
      '| e.g. (0.0).1 =', f(st, 3)(f(st, 3)(0, 0), 1), 'but 0.(0.1) =', f(st, 3)(0, f(st, 3)(0, 1)))
print('         smallest idempotent non-associative magma has', next(
    k for k in range(2, 5) if any(holds(lambda x: (f(op, k)(x, x), x), k, 1) and not assoc(op, k) for op in ops(k))),
    'elements')

# Ex. 5.x: lattices on 3 elements (labelled), via semilattices first
n = 3
semi = [op for op in ops(n) if holds(lambda x: (f(op, n)(x, x), x), n, 1)
        and holds(lambda x, y: (f(op, n)(x, y), f(op, n)(y, x)), n, 2) and assoc(op, n)]
lat = sum(1 for F in semi for G in semi
          if holds(lambda x, y: (f(F, n)(x, f(G, n)(x, y)), x), n, 2) and holds(lambda x, y: (f(G, n)(x, f(F, n)(x, y)), x), n, 2))
print('Ex. 5.1  semilattice operations on 3 elements:', len(semi), '| lattices (join, meet) on 3 labelled elements:', lat)

# Ex. 6.x: x o y := y . x plus associativity of . gives associativity of o
n = 3
ok = True
for F in ops(n):
    if not assoc(F, n): continue
    G = tuple(F[y * n + x] for x in range(n) for y in range(n))
    if not assoc(G, n): ok = False; break
print('Ex. 6.2  on 3 elements: every associative . has an associative transpose:', ok)

# Ex. 7.x: rectangular band on I x J = {0,1} x {0,1}, elements coded 2*i + j
el = [(i, j) for i in range(2) for j in range(2)]
code = {e: k for k, e in enumerate(el)}
rb = tuple(code[(el[x][0], el[y][1])] for x in range(4) for y in range(4))
tr = tuple(rb[y * 4 + x] for x in range(4) for y in range(4))
d, o = f(rb, 4), f(tr, 4)
print('Ex. 7.1  rectangular band 2x2: associative', assoc(rb, 4), '| idempotent', holds(lambda x: (d(x, x), x), 4, 1),
      '| x.(y.x) = x', holds(lambda x, y: (d(x, d(y, x)), x), 4, 2), '| (x.y).z = x.z', holds(lambda x, y, z: (d(d(x, y), z), d(x, z)), 4, 3))
L31 = [lambda x, y: (d(x, o(x, y)), x), lambda x, y: (d(o(x, y), y), y),
       lambda x, y: (d(d(x, x), d(y, x)), x), lambda x, y: (d(d(x, y), d(x, x)), x)]
print('Ex. 7.2  with x o y := y . x, the four laws of 31d6d970 hold:', [holds(l, 4, 2) for l in L31])

# Ex. 1.x: injective but not surjective needs an infinite set
print('Ex. 1.3  injective self-maps of {0,1,2} that are not surjective:',
      sum(1 for p in itertools.product(range(3), repeat=3) if len(set(p)) == 3 and set(p) != {0, 1, 2}),
      '| injective ones:', sum(1 for p in itertools.product(range(3), repeat=3) if len(set(p)) == 3))

# Ex. 1.1, 1.2: products and functions between small sets
print('Ex. 1.1  |{0,1} x {0,1,2}| =', len(list(itertools.product(range(2), range(3)))))
fs = list(itertools.product(range(2), repeat=3))   # functions {0,1,2} -> {0,1}
print('Ex. 1.2  functions {0,1,2} -> {0,1}:', len(fs), '| injective:', sum(1 for p in fs if len(set(p)) == 3),
      '| surjective:', sum(1 for p in fs if set(p) == {0, 1}))

# Ex. 2.3: idempotent operations on 2 elements
print('Ex. 2.2  idempotent operations on {0,1}:', [NAMES.get(op, op) for op in ops(2) if holds(lambda x: (f(op, 2)(x, x), x), 2, 1)])

# Ex. 5.2: the duals of x.(x o y) = x, checked semantically on all 256 pairs on {0,1}:
# e holds in (., o) iff swap(e) holds in (o, .), iff opp.(e) holds in (.^T, o), iff opp o(e) holds in (., o^T)
def T_(op, n): return tuple(op[y * n + x] for x in range(n) for y in range(n))
e      = lambda a, b: lambda x, y: (a(x, b(x, y)), x)          # x.(x o y) = x
swap   = lambda a, b: lambda x, y: (b(x, a(x, y)), x)          # x o (x . y) = x
opp_d  = lambda a, b: lambda x, y: (a(b(x, y), x), x)          # (x o y) . x = x
opp_o  = lambda a, b: lambda x, y: (a(x, b(y, x)), x)          # x . (y o x) = x
opp_do = lambda a, b: lambda x, y: (a(b(y, x), x), x)          # (y o x) . x = x
good = True
for F in ops(2):
    for G in ops(2):
        a, b, aT, bT = f(F, 2), f(G, 2), f(T_(F, 2), 2), f(T_(G, 2), 2)
        h = holds(e(a, b), 2, 2)
        good &= h == holds(swap(b, a), 2, 2) == holds(opp_d(aT, b), 2, 2) == holds(opp_o(a, bT), 2, 2) == holds(opp_do(aT, bT), 2, 2)
print('Ex. 5.2  the four duals of x.(x o y) = x agree with the relabelled structures on all 256 pairs:', good)

# Ex. 7.3: a split theory that implies a bridge, through degenerate models
print('Ex. 7.3  every pair on {0,1,2} with x.y = x and x o y = x satisfies x.y = x o y:',
      all(F[x * 3 + y] == G[x * 3 + y] for F in [tuple(x for x in range(3) for y in range(3))]
          for G in [tuple(x for x in range(3) for y in range(3))] for x in range(3) for y in range(3)))

# Ex. 7.4: a split theory in disguise. T = {x.(x.y) = y, x.(y o z) = x.(z o y)} has the same models as
# T' = {x.(x.y) = y, y o z = z o y} (left translations of . are injective, so the bridge says o is commutative)
for n in (2, 3):
    good, cnt = True, 0
    invol = [F for F in ops(n) if holds(lambda x, y: (f(F, n)(x, f(F, n)(x, y)), y), n, 2)]
    for F in invol:
        for G in ops(n):
            a, b = f(F, n), f(G, n)
            t = holds(lambda x, y, z: (a(x, b(y, z)), a(x, b(z, y))), n, 3)
            t2 = holds(lambda y, z: (b(y, z), b(z, y)), n, 2)
            good &= t == t2; cnt += t
    print(f'Ex. 7.4  on {n} elements: {len(invol)} operations with x.(x.y) = y; T and T\' have the same models: {good} ({cnt} models)')

# Section 8 exercise: how many pairs of laws
import math
print('Ex. 8.1  pairs of distinct laws among 71,369:', f'{math.comb(71369, 2):,}', '| sets of 4:', f'{math.comb(71369, 4):.3e}')
