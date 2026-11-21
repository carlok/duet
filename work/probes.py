"""Probe corpus: finite structures (A, f, g) with two binary operations, carriers 2..6."""
import itertools, random
import numpy as np
random.seed(20261120); rng = np.random.default_rng(20261120)
NMAX = 6

def affine(n):
    return {f'aff{n}[{a},{b},{c}]': np.array([[(a*x+b*y+c) % n for y in range(n)] for x in range(n)])
            for a in range(n) for b in range(n) for c in range(n)}

def chain_lattice(n):
    return {f'min{n}': np.array([[min(x,y) for y in range(n)] for x in range(n)]),
            f'max{n}': np.array([[max(x,y) for y in range(n)] for x in range(n)])}

def lattice_from_order(name, n, leq):
    meet = np.zeros((n,n),int); join = np.zeros((n,n),int)
    for x in range(n):
        for y in range(n):
            lows = [z for z in range(n) if leq(z,x) and leq(z,y)]
            ups = [z for z in range(n) if leq(x,z) and leq(y,z)]
            meet[x,y] = [z for z in lows if all(leq(w,z) for w in lows)][0]
            join[x,y] = [z for z in ups if all(leq(z,w) for w in ups)][0]
    return {f'{name}.meet': meet, f'{name}.join': join}

def group_ops(name, elems, mul, inv):
    n = len(elems); idx = {e:i for i,e in enumerate(elems)}
    M = lambda a,b: idx[mul(elems[a],elems[b])]; I = lambda a: idx[inv(elems[a])]
    forms = {'xy': lambda x,y: M(x,y), 'yx': lambda x,y: M(y,x), 'xy^-1': lambda x,y: M(x,I(y)),
             'x^-1y': lambda x,y: M(I(x),y), 'y^-1xy': lambda x,y: M(M(I(y),x),y),
             'yxy^-1': lambda x,y: M(M(y,x),I(y)), 'yx^-1y': lambda x,y: M(M(y,I(x)),y),
             'xy^-1x': lambda x,y: M(M(x,I(y)),x), 'x^-1y^-1': lambda x,y: M(I(x),I(y)),
             'x^-1yx': lambda x,y: M(M(I(x),y),x)}
    return {f'{name}.{k}': np.array([[f(x,y) for y in range(n)] for x in range(n)]) for k,f in forms.items()}

def menu(n):
    m = {}
    m.update(affine(n)); m.update(chain_lattice(n))
    return m

def build():
    probes = []  # (name, n, F, G)
    # carrier 2: every pair of tables
    tabs2 = [np.array(t).reshape(2,2) for t in itertools.product(range(2), repeat=4)]
    for i,a in enumerate(tabs2):
        for j,b in enumerate(tabs2): probes.append((f'all2[{i},{j}]', 2, a, b))
    # carrier 3: all pairs from the affine+chain menu, plus random pairs
    m3 = list(menu(3).items())
    for (na,a),(nb,b) in itertools.product(m3, m3): probes.append((f'{na}|{nb}', 3, a, b))
    for k in range(1500):
        probes.append((f'rand3[{k}]', 3, rng.integers(0,3,(3,3)), rng.integers(0,3,(3,3))))
    # carrier 4: Z/4 affine, F4 linear, Klein group ops, chain and Boolean lattice; sampled pairs
    F4mul = [[0,0,0,0],[0,1,2,3],[0,2,3,1],[0,3,1,2]]
    m4 = dict(menu(4))
    for a in range(4):
        for b in range(4):
            for c in range(4):
                m4[f'F4[{a},{b},{c}]'] = np.array([[F4mul[a][x] ^ F4mul[b][y] ^ c for y in range(4)] for x in range(4)])
    klein = [(0,0),(0,1),(1,0),(1,1)]
    m4.update(group_ops('V4', klein, lambda p,q: ((p[0]+q[0])%2,(p[1]+q[1])%2), lambda p: p))
    m4.update(lattice_from_order('B2', 4, lambda x,y: (x & y) == x))
    k4 = list(m4.items())
    for (na,a),(nb,b) in random.sample(list(itertools.product(k4,k4)), 5000): probes.append((f'{na}|{nb}', 4, a, b))
    # pairs that are lattices / rings by construction (meet, join), (join, meet), (+, *) on Z/n
    for n in (3,4,5,6):
        add = np.array([[(x+y)%n for y in range(n)] for x in range(n)]); mul = np.array([[(x*y)%n for y in range(n)] for x in range(n)])
        probes += [(f'Z{n}(+,*)', n, add, mul), (f'Z{n}(*,+)', n, mul, add)]
    for name,n,leq in [('M3',5,lambda x,y: x==y or x==0 or y==4), ('N5',5,lambda x,y: x==y or x==0 or y==4 or (x,y)==(1,2))]:
        L = lattice_from_order(name, n, leq); a,b = L[f'{name}.meet'], L[f'{name}.join']
        probes += [(f'{name}(meet,join)', n, a, b), (f'{name}(join,meet)', n, b, a)]
    # carrier 5: affine pairs, sampled
    k5 = list(menu(5).items())
    for (na,a),(nb,b) in random.sample(list(itertools.product(k5,k5)), 3000): probes.append((f'{na}|{nb}', 5, a, b))
    # carrier 6: S3 and Z/6 group-derived operations, all pairs; plus Z/6 affine sample
    perms = list(itertools.permutations(range(3)))
    s3 = group_ops('S3', perms, lambda p,q: tuple(p[q[i]] for i in range(3)), lambda p: tuple(sorted(range(3), key=lambda i: p[i])))
    z6 = group_ops('Z6', list(range(6)), lambda a,b: (a+b)%6, lambda a: (-a)%6)
    g6 = list(s3.items()) + list(z6.items())
    for (na,a),(nb,b) in itertools.product(g6, g6): probes.append((f'{na}|{nb}', 6, a, b))
    k6 = list(affine(6).items())
    for (na,a),(nb,b) in random.sample(list(itertools.product(k6,k6)), 1500): probes.append((f'{na}|{nb}', 6, a, b))
    return probes

if __name__ == '__main__':
    ps = build(); import collections
    print(len(ps), collections.Counter(n for _,n,_,_ in ps))
