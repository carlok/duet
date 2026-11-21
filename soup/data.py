"""The law x structure matrix and its metadata, loaded once per process.

The two packed bit matrices (~111 MB each) are memory-mapped read-only, so every process in the
container shares the same page-cache pages instead of holding a private copy.
"""
import pickle
import numpy as np
from .paths import data

meta = pickle.load(open(data('meta.pkl'), 'rb'))
LAWS = meta['laws']
ORDER = np.array(meta['order'])
PROBES = meta['probes']
TREES = meta['law_trees']
PM = np.load(data('M_probe_major.npy'), mmap_mode='r')   # probes x ceil(L/8), bits = laws
LM = np.load(data('M_law_major.npy'), mmap_mode='r')     # laws x ceil(P/8), bits = probes
NL, NP = len(LAWS), len(PROBES)
LAW_INDEX = {s: i for i, s in enumerate(LAWS)}
SIZES = np.array([n for _, n in PROBES])


def _nondeg():
    """Base structures with two distinct, essentially binary operations (cached next to the matrix)."""
    p = data('nondeg.npy')
    try:
        m = np.load(p)
        if m.shape == (NP,):
            return m
    except FileNotFoundError:
        pass
    from .probes import build
    from .matrix import nondeg_mask
    m = nondeg_mask(build())
    np.save(p, m)
    return m


NONDEG = _nondeg()


def unpack_probes(bits): return np.unpackbits(bits)[:NP].astype(bool)
def unpack_laws(bits): return np.unpackbits(bits)[:NL].astype(bool)
def nvars_tree(t): return t[1] + 1 if t[0] == 'v' else max(nvars_tree(t[1]), nvars_tree(t[2]))


def sat_base(T):
    """Packed probe bits of the base structures satisfying every law of T."""
    T = list(T)
    return np.bitwise_and.reduce(LM[T], axis=0) if T else np.full(LM.shape[1], 255, np.uint8)


def tptp(t):
    if t[0] == 'v': return 'XYZWUV'[t[1]]
    return ('f' if t[0] == 'f' else 'g') + '(' + tptp(t[1]) + ',' + tptp(t[2]) + ')'


def fof(i, name, role):
    """Law i as a TPTP first-order formula (for external provers, T2)."""
    L, R = TREES[i]
    vs = sorted({c for c in tptp(L) + tptp(R) if c in 'XYZWUV'})
    body = tptp(L) + ' = ' + tptp(R)
    return f"fof({name},{role},{('! [' + ','.join(vs) + '] : ') if vs else ''}({body}))."
