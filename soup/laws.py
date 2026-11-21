"""Enumerate equational laws over k binary operation symbols, up to relabelling and side swap.
Terms: ('v', i) or (op, left, right). Order = total number of operation nodes in the law."""
import itertools, functools, sys

@functools.lru_cache(None)
def shapes(n):  # binary trees with n internal nodes, leaves as None
    if n == 0: return [None]
    out = []
    for i in range(n):
        for l in shapes(i):
            for r in shapes(n-1-i): out.append(('*', l, r))
    return out

def leaves(t): return 1 if t is None else leaves(t[1]) + leaves(t[2])
def nodes(t): return 0 if t is None else 1 + nodes(t[1]) + nodes(t[2])

def label(t, ops, vs):
    # ops: iterator over op labels (preorder), vs: iterator over var ids (in-order leaves)
    if t is None: return ('v', next(vs))
    o = next(ops); l = label(t[1], ops, vs); r = label(t[2], ops, vs)
    return (o, l, r)

def rgs(n):  # restricted growth strings = set partitions of n leaves
    def rec(prefix, m):
        if len(prefix) == n: yield tuple(prefix); return
        for v in range(m + 1): yield from rec(prefix + [v], max(m, v + 1) if v == m else m)
    yield from rec([], 0)

def canon_vars(lhs, rhs):
    mp = {}
    def walk(t):
        if t[0] == 'v':
            if t[1] not in mp: mp[t[1]] = len(mp)
            return ('v', mp[t[1]])
        return (t[0], walk(t[1]), walk(t[2]))
    a = walk(lhs); b = walk(rhs); return a, b

def key(lhs, rhs):
    a = canon_vars(lhs, rhs); b = canon_vars(rhs, lhs)
    b = (b[1], b[0]) if False else b
    return min(repr(a), repr((b[1], b[0])) if False else repr(b))

def enumerate_laws(max_order, opsyms):
    seen = {}
    for total in range(max_order + 1):
        for nl in range(total + 1):
            nr = total - nl
            if nl < nr: continue  # side swap handled by canonical key anyway, halve work
            for sl in shapes(nl):
                for sr in shapes(nr):
                    nleaves = leaves(sl) + leaves(sr)
                    for ol in itertools.product(opsyms, repeat=nl):
                        for orr in itertools.product(opsyms, repeat=nr):
                            for g in rgs(nleaves):
                                it = iter(g)
                                L = label(sl, iter(ol), it); R = label(sr, iter(orr), it)
                                if L == R: continue
                                k1 = repr(canon_vars(L, R)); k2 = repr(canon_vars(R, L))
                                k = min(k1, k2)
                                if k not in seen: seen[k] = (L, R) if k == k1 else canon_vars(R, L)
    return seen

if __name__ == '__main__':
    for order in range(5):
        one = enumerate_laws(order, ('f',))
        print('one op, order <=', order, len(one) + 1)   # +1 for x = x
