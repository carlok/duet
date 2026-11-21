"""Syntactic duality invariance of a theory: swap the operations, take opposites, or both."""
import sys; sys.path.insert(0, '/home/claude/soup')
from named import KEY, meta
from laws import canon_vars
TREES = meta['law_trees']
def tr(t, swap, opp):
    if t[0] == 'v': return t
    op = {'f': 'g', 'g': 'f'}[t[0]] if swap else t[0]
    l, r = tr(t[1], swap, opp), tr(t[2], swap, opp)
    return (op, r, l) if opp else (op, l, r)
def image(i, swap, opp):
    L, R = TREES[i]; L2, R2 = tr(L, swap, opp), tr(R, swap, opp)
    return KEY[min(repr(canon_vars(L2, R2)), repr(canon_vars(R2, L2)))]
def dualities(T):
    S = set(T); out = []
    for name, sw, op in [('swap', 1, 0), ('opposite', 0, 1), ('swap+opposite', 1, 1)]:
        if {image(t, sw, op) for t in T} == S: out.append(name)
    return out
