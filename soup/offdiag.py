"""Off-diagonal synergy, the 2-element-lattice exclusion and one-operation pools (arm 'fusion', run X4, 22 Nov 2026).

Up to X3, 70% of the 3,574 theories with a positive verified score proved an emergent law in one variable
(x·x = x, x·x = x∘x, x·(x·x) = x·x, ...), and none proved emergent associativity. The search rewarded what a fusion
forces on the diagonal. The lattice absorption pair, the reference case, is itself such a case.

Off-diagonal gain: laws implied by T on the corpus that no single law t of T implies even together with all
diagonal laws D that T implies:

    G(T) = implied(T) minus the union over t in T of implied({t} | D),   D = diagonal laws in implied(T).

A law is diagonal if each side has at most one variable: x·x = x, x·x = x∘x, x·(x·x) = x·x, and also x·x = y·y,
x·(x·x) = y·y. Such a law speaks only about the terms in one variable, the squares and their kin. The first version
(X4 attempt x4a, 22 Nov 2026 12:55 UTC) used one-variable laws only. In three minutes the search moved to
x·x = y·y (10 of 18 positive results), so the definition was widened (PREREGISTRATION.md, deviation 6).

So a law counts only if the fusion produces it by some route other than first forcing something about x·x and x∘x.
Every law of D lies in each implied({t} | D), so diagonal laws never count. As for fusion_gain, non-implication by
{t} | D is witnessed by a corpus structure, a real finite model. D is read from the corpus, so it may contain a
claim that is false. That can only remove laws from G, never add any.

LAT2 is the law vector of the 2-element lattice (· = join, ∘ = meet; the swapped pair is isomorphic to it through
0 <-> 1). A theory all of whose laws hold there is a fragment of distributive-lattice theory, or something weaker.
The fusion arm skips those theories: that corner is mapped.

Pools: the one-operation laws that serve as "traditions" for the fusion arm's proposal operator. A law qualifies if its
corpus models include a non-degenerate structure at three or more sizes. Within each operation, the more restrictive
half (fewer corpus models) is kept.
"""
import numpy as np

from .core import TREES, NL, law_vector
from .data import PM, unpack_laws


def _vars(t): return {t[1]} if t[0] == 'v' else _vars(t[1]) | _vars(t[2])
def _ops(t): return set() if t[0] == 'v' else {t[0]} | _ops(t[1]) | _ops(t[2])


ONEVAR = np.array([len(_vars(L) | _vars(R)) == 1 for L, R in TREES])
DIAG = np.array([len(_vars(L)) <= 1 and len(_vars(R)) <= 1 for L, R in TREES])   # each side in one variable
OPS = [_ops(L) | _ops(R) for L, R in TREES]
ONLY_F = np.array([o == {'f'} for o in OPS])     # laws in · alone
ONLY_G = np.array([o == {'g'} for o in OPS])     # laws in ∘ alone

_LAT2 = None


def lat2():
    """Bool vector: the laws that hold in the 2-element lattice (· = max, ∘ = min)."""
    global _LAT2
    if _LAT2 is None:
        _LAT2 = law_vector(np.array([[0, 1], [1, 1]]), np.array([[0, 0], [0, 1]]), 2)
    return _LAT2


def _implied_from(C, base, ext):
    rows = [PM[base], C.XP[ext]]
    rows = [r for r in rows if r.shape[0]]
    if not rows: return None
    acc = np.bitwise_and.reduce(rows[0], axis=0)
    if len(rows) > 1: acc &= np.bitwise_and.reduce(rows[1], axis=0)
    return unpack_laws(acc)


def offdiag_gain(C, T, imp=None):
    """Indices of the off-diagonal emergent laws of T on corpus C (see the module docstring); None without models."""
    T = sorted(set(T))
    if imp is None: imp = C.implied(T)
    if imp is None: return None
    D = np.flatnonzero(imp & DIAG).tolist()
    covered = imp & DIAG
    bD, eD = C.sat(D) if D else (None, None)
    for t in T:
        b, e = C.sat([t])
        if bD is not None: b, e = b & bD, e & eD
        s = _implied_from(C, b, e)
        if s is not None: covered |= s
    return np.flatnonzero(imp & ~covered)


def pools(C, keep=0.5):
    """(pool of · laws, pool of ∘ laws) as sorted index lists; see the module docstring."""
    out = []
    for mask in (ONLY_F, ONLY_G):
        cand = []
        for t in np.flatnonzero(mask):
            m, nd, sizes = C.stats([int(t)])
            if nd and len(sizes) >= 3: cand.append((m, int(t)))
        cand.sort()
        out.append(sorted(t for _, t in cand[:max(1, int(len(cand) * keep))]))
    return tuple(out)
