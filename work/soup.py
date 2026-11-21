import numpy as np, pickle
meta = pickle.load(open('/home/claude/soup/meta.pkl','rb'))
LAWS = meta['laws']; ORDER = np.array(meta['order']); PROBES = meta['probes']
PM = np.load('/home/claude/soup/M_probe_major.npy')   # probes x ceil(L/8)
LM = np.load('/home/claude/soup/M_law_major.npy')     # laws x ceil(P/8)
NL, NP = len(LAWS), len(PROBES)
idx = {s:i for i,s in enumerate(LAWS)}
SIZES = np.array([n for _,n in PROBES])

def unpack_probes(bits): return np.unpackbits(bits)[:NP].astype(bool)
def unpack_laws(bits): return np.unpackbits(bits)[:NL].astype(bool)

def sat(T):
    b = np.bitwise_and.reduce(LM[list(T)], axis=0) if len(T) else np.full(LM.shape[1], 255, np.uint8)
    return b
def implied(T, satbits=None):
    s = unpack_probes(sat(T) if satbits is None else satbits)
    rows = PM[s]
    if rows.shape[0] == 0: return None
    return np.bitwise_and.reduce(rows, axis=0)
def emergent(T):
    imp = implied(T)
    if imp is None: return None, 0
    union = np.zeros_like(imp)
    for i in range(len(T)):
        sub = [t for j,t in enumerate(T) if j != i]
        si = implied(sub)
        if si is not None: union |= si
    em = imp & ~union
    return unpack_laws(em), int(unpack_probes(sat(T)).sum())

import subprocess, tempfile, os
TREES = meta['law_trees']
def tptp(t):
    if t[0] == 'v': return 'XYZWUV'[t[1]]
    return ('f' if t[0] == 'f' else 'g') + '(' + tptp(t[1]) + ',' + tptp(t[2]) + ')'
def fof(i, name, role):
    L, R = TREES[i]
    vs = sorted({c for c in tptp(L) + tptp(R) if c in 'XYZWUV'})
    body = tptp(L) + ' = ' + tptp(R)
    return f"fof({name},{role},{('! [' + ','.join(vs) + '] : ') if vs else ''}({body}))."
def prove(T, goal, timeout=10):
    """True = E proves goal from T; False = E finds no proof (timeout/satisfiable)."""
    src = '\n'.join(fof(t, f'a{k}', 'axiom') for k, t in enumerate(T)) + '\n' + fof(goal, 'goal', 'conjecture') + '\n'
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh: fh.write(src); path = fh.name
    try:
        r = subprocess.run(['eprover', '--auto', '--silent', f'--cpu-limit={timeout}', path], capture_output=True, text=True, timeout=timeout + 5)
        return 'SZS status Theorem' in r.stdout
    except subprocess.TimeoutExpired: return False
    finally: os.unlink(path)

from probes import build
_P = build()
def _deg(T, n):
    proj1 = all(T[x, y] == x for x in range(n) for y in range(n)); proj2 = all(T[x, y] == y for x in range(n) for y in range(n))
    const = len({int(v) for v in T.flatten()}) == 1
    return proj1 or proj2 or const
NONDEG = np.array([not _deg(F, n) and not _deg(G, n) and not np.array_equal(F, G) for _, n, F, G in _P])

import z3
_S = z3.DeclareSort('S'); _f = z3.Function('f', _S, _S, _S); _g = z3.Function('g', _S, _S, _S)
def _zt(t, env):
    if t[0] == 'v': return env[t[1]]
    return (_f if t[0] == 'f' else _g)(_zt(t[1], env), _zt(t[2], env))
def _zlaw(i, consts=None):
    L, R = TREES[i]; n = max(nvars_tree(L), nvars_tree(R))
    if consts is not None: env = consts[:n]; return _zt(L, env) == _zt(R, env)
    vs = [z3.Const(f'v{k}', _S) for k in range(n)]
    body = _zt(L, vs) == _zt(R, vs)
    return z3.ForAll(vs, body) if vs else body
def nvars_tree(t): return t[1] + 1 if t[0] == 'v' else max(nvars_tree(t[1]), nvars_tree(t[2]))
def zprove(T, goal, ms=5000):
    s = z3.Solver(); s.set('timeout', ms)
    for t in T: s.add(_zlaw(t))
    sk = [z3.Const(f'c{k}', _S) for k in range(6)]
    s.add(z3.Not(_zlaw(goal, sk)))
    r = s.check()
    return r == z3.unsat
prove = zprove

def _essbin(T, n):
    dep_x = any(T[x1, y] != T[x2, y] for y in range(n) for x1 in range(n) for x2 in range(n))
    dep_y = any(T[x, y1] != T[x, y2] for x in range(n) for y1 in range(n) for y2 in range(n))
    return dep_x and dep_y
NONDEG = np.array([_essbin(F, n) and _essbin(G, n) and not np.array_equal(F, G) for _, n, F, G in _P])
