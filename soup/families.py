"""Countermodels from structured families, for claims that finite search to small sizes cannot settle.

  cyclic(T, goal, n)       translation-invariant models on Z/n: x.y = x + F[y - x], x o y = x + G[y - x]
                           (mod n). Translation invariance means a law holds iff it holds with its first
                           variable at 0, so each law gives n^(k-1) ground constraints on 2n unknowns.
  z_piecewise(T, goal, W)  translation-invariant models on Z with F, G linear outside the window |d| <= W
                           (slopes enumerated, offsets and window values solved by z3), found by CEGAR:
                           candidates from finitely many instances, then a proof over all of Z (linear
                           integer arithmetic) or a counterexample instance that is added back.
Both are standard model families in equational-logic search (the Equational Theories Project uses them);
the offline LLM of 21 Nov 2026 also used them (cyclic to n = 16 on S12). The code here is our own.
Every model returned is re-checked: cyclic tables with core.law_vector, Z-models by the proof over Z.
"""
import itertools

import numpy as np
import z3

from .data import TREES


def _nv(t): return t[1] + 1 if t[0] == 'v' else max(_nv(t[1]), _nv(t[2]))
def law_k(i): L, R = TREES[i]; return max(_nv(L), _nv(R))


def ev(t, env, f, g):
    if t[0] == 'v': return env[t[1]]
    a, b = ev(t[1], env, f, g), ev(t[2], env, f, g)
    return f(a, b) if t[0] == 'f' else g(a, b)


# ---- cyclic Z/n

def cyclic(T, goal, n, timeout_ms=600_000):
    """A translation-invariant model on Z/n of T violating goal: (F, G) Cayley tables, None (no such model
    in the family) or 'unknown'."""
    D = z3.BitVecSort(16)
    Fz = z3.Function('F', D, D); Gz = z3.Function('G', D, D)
    N = z3.BitVecVal(n, 16)
    md = lambda e: z3.URem(e, N)
    f = lambda a, b: md(a + Fz(md(b - a + N)))
    g = lambda a, b: md(a + Gz(md(b - a + N)))
    s = z3.SolverFor('QF_UFBV'); s.set('timeout', timeout_ms)
    for d in range(n):
        s.add(z3.ULT(Fz(z3.BitVecVal(d, 16)), N), z3.ULT(Gz(z3.BitVecVal(d, 16)), N))
    for t in T:
        L, R = TREES[t]
        for rest in itertools.product(range(n), repeat=law_k(t) - 1):
            env = [z3.BitVecVal(0, 16)] + [z3.BitVecVal(v, 16) for v in rest]
            s.add(ev(L, env, f, g) == ev(R, env, f, g))
    L, R = TREES[goal]
    s.add(z3.Or([ev(L, [z3.BitVecVal(0, 16)] + [z3.BitVecVal(v, 16) for v in rest], f, g) !=
                 ev(R, [z3.BitVecVal(0, 16)] + [z3.BitVecVal(v, 16) for v in rest], f, g)
                 for rest in itertools.product(range(n), repeat=law_k(goal) - 1)]))
    r = s.check()
    if r == z3.unsat: return None
    if r != z3.sat: return 'unknown'
    m = s.model()
    Fv = [m.eval(Fz(z3.BitVecVal(d, 16)), model_completion=True).as_long() for d in range(n)]
    Gv = [m.eval(Gz(z3.BitVecVal(d, 16)), model_completion=True).as_long() for d in range(n)]
    F = np.array([[(x + Fv[(y - x) % n]) % n for y in range(n)] for x in range(n)])
    G = np.array([[(x + Gv[(y - x) % n]) % n for y in range(n)] for x in range(n)])
    return F, G


def check_tables(T, goal, F, G):
    from .core import law_vector
    lv = law_vector(F, G, len(F))
    return all(lv[t] for t in T) and not lv[goal]


# ---- piecewise-linear on Z

def _pw(d, slope_hi, off_hi, slope_lo, off_lo, win, W):
    e = z3.If(d > W, slope_hi * d + off_hi, slope_lo * d + off_lo)
    for k in range(-W, W + 1):
        e = z3.If(d == k, win[k + W], e)
    return e


def _ops(P, W):
    f = lambda a, b: a + _pw(b - a, *P['F'], W)
    g = lambda a, b: a + _pw(b - a, *P['G'], W)
    return f, g


def z_piecewise(T, goal, W=2, slopes=range(-2, 3), bound=12, rounds=60, timeout_ms=60_000, deadline=None):
    """Search a model on Z with x.y = x + F(y-x), x o y = x + G(y-x), F and G linear for d > W and d < -W.
    Returns a dict of parameters (a model proved over Z), None (nothing in the family) or 'unknown'.
    deadline: a time.time() value after which the search stops and reports 'unknown'."""
    import time
    gk = law_k(goal); any_unknown = False
    for sF in itertools.product(slopes, repeat=2):
        for sG in itertools.product(slopes, repeat=2):
            if deadline and time.time() > deadline: return 'unknown'
            ints = lambda p, k: [z3.Int(f'{p}{i}') for i in range(k)]
            oF, oG = ints('oF', 2), ints('oG', 2); wF, wG = ints('wF', 2 * W + 1), ints('wG', 2 * W + 1)
            P = {'F': (sF[0], oF[0], sF[1], oF[1], wF), 'G': (sG[0], oG[0], sG[1], oG[1], wG)}
            f, g = _ops(P, W)
            s = z3.Solver(); s.set('timeout', timeout_ms)
            for v in oF + oG + wF + wG: s.add(v >= -bound, v <= bound)
            L, R = TREES[goal]; zero = [z3.IntVal(0)] * gk
            s.add(ev(L, zero, f, g) != ev(R, zero, f, g))           # claim fails at 0 (translation invariance)
            inst = [(t, (0,) + rest) for t in T for rest in itertools.product(range(-2, 3), repeat=law_k(t) - 1)]
            for t, e in inst:
                L, R = TREES[t]; s.add(ev(L, [z3.IntVal(v) for v in e], f, g) == ev(R, [z3.IntVal(v) for v in e], f, g))
            for _ in range(rounds):
                r = s.check()
                if r == z3.unsat: break
                if r != z3.sat: any_unknown = True; break
                m = s.model()
                val = lambda v: m.eval(v, model_completion=True).as_long()
                Pc = {'F': (sF[0], val(oF[0]), sF[1], val(oF[1]), [val(v) for v in wF]),
                      'G': (sG[0], val(oG[0]), sG[1], val(oG[1]), [val(v) for v in wG])}
                fc, gc = _ops({k: (a, z3.IntVal(b), c, z3.IntVal(d), [z3.IntVal(x) for x in w])
                               for k, (a, b, c, d, w) in Pc.items()}, W)
                cex = None
                for t in T:          # proof over Z, or a counterexample instance
                    L, R = TREES[t]; xs = [z3.Int(f'x{i}') for i in range(law_k(t))]
                    v = z3.Solver(); v.set('timeout', timeout_ms); v.add(ev(L, xs, fc, gc) != ev(R, xs, fc, gc))
                    rv = v.check()
                    if rv == z3.sat:
                        mv = v.model(); e = [mv.eval(x, model_completion=True).as_long() for x in xs]
                        cex = (t, tuple(x - e[0] for x in e)); break
                    if rv != z3.unsat: cex = 'unknown'; break
                if cex is None: return {'W': W, 'params': Pc}
                if cex == 'unknown': any_unknown = True; break
                t, e = cex; L, R = TREES[t]
                s.add(ev(L, [z3.IntVal(x) for x in e], f, g) == ev(R, [z3.IntVal(x) for x in e], f, g))
            else:
                any_unknown = True
    return 'unknown' if any_unknown else None
