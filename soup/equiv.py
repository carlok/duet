"""Is a theory a known variety in disguise? Equivalence, both ways, with a list of standard two-operation theories
(PREREGISTRATION.md, T5a ranking step 1).

    equivalent(T, C) -> list of names of standard theories with the same equational consequences as T

The list:
- the named theories of T3 (calib.NAMED) and distributive lattices, on both assignments of the operations;
- pairs (V on ·, W on ∘) with no bridge law, for V, W among semilattices, bands, rectangular bands, left-zero
  bands, right-zero bands and 'no law'.

A screen on the corpus comes first. If some structure satisfies one side and fails a law of the other, the two are
not equivalent; this is free. E then proves every law of each side from the other (30 s, 500,000 processed clauses
each). Only a complete set of proofs counts as equivalence.
"""
import itertools

ONE = {
    'semilattice': ['(x·y)·z = x·(y·z)', 'x·y = y·x', 'x·x = x'],
    'band': ['(x·y)·z = x·(y·z)', 'x·x = x'],
    'rectangular band': ['(x·y)·z = x·(y·z)', 'x·x = x', '(x·y)·z = x·z'],
    'left-zero band': ['x·y = x'],
    'right-zero band': ['x·y = y'],
    'no law': [],
}


def _swap(s): return s.replace('·', '#').replace('∘', '·').replace('#', '∘')


def standard():
    from .calib import NAMED
    out = {}
    named = dict(NAMED)
    named['distributive lattice'] = NAMED['lattice'] + ['x·(y∘z) = (x·y)∘(x·z)']
    for name, laws in named.items():
        out[name] = laws
        out[name + ' (operations swapped)'] = [_swap(s) for s in laws]
    for (a, la), (b, lb) in itertools.product(ONE.items(), repeat=2):
        if a == b == 'no law': continue
        out[f'{a} on ·, {b} on ∘'] = la + [_swap(s) for s in lb]
    return out


def _prove_all(A, B, secs=30):
    from .provers import prove_e
    for b in B:
        if b in A: continue
        if prove_e(sorted(A), b, processed_limit=500_000, cpu_limit=secs)['status'] != 'proved': return False
    return True


def equivalent(T, C, secs=30):
    from .named import law_index
    T = sorted(set(T)); found = []
    impT = C.implied(T)
    for name, laws in standard().items():
        V = {law_index(s.replace(' ', '')) for s in laws}
        if None in V: continue                      # a law beyond order 4: not comparable here
        V = sorted(V)
        if impT is not None and not all(impT[v] for v in V): continue            # a corpus model of T fails V
        impV = C.implied(V) if V else None
        if impV is not None and not all(impV[t] for t in T): continue            # a corpus model of V fails T
        if _prove_all(T, V, secs) and _prove_all(V, T, secs): found.append(name)
    return found
