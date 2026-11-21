"""Compute the law x probe satisfaction matrix with numba; save packed bit matrices."""
import numpy as np, numba as nb, time, pickle
from laws import enumerate_laws
from probes import build, NMAX

def postfix(t, out):
    if t[0] == 'v': out.append(t[1]); return
    postfix(t[1], out); postfix(t[2], out); out.append(10 if t[0] == 'f' else 11)

def render(t, top=True):
    if t[0] == 'v': return 'xyzwuv'[t[1]]
    s = render(t[1], False) + (' · ' if t[0] == 'f' else ' ∘ ') + render(t[2], False)
    return s if top else '(' + s + ')'

def nvars(t): return 0 if False else (t[1] + 1 if t[0] == 'v' else max(nvars(t[1]), nvars(t[2])))

@nb.njit(cache=True)
def run(prog, a, b, assign, F, G):
    stack = np.empty(16, np.int64); sp = 0
    for k in range(a, b):
        tok = prog[k]
        if tok < 10: stack[sp] = assign[tok]; sp += 1
        else:
            y = stack[sp-1]; x = stack[sp-2]; sp -= 1
            stack[sp-1] = F[x, y] if tok == 10 else G[x, y]
    return stack[0]

@nb.njit(parallel=True, cache=True)
def evaluate(prog, lo, mid, hi, nv, Fs, Gs, sizes):
    P = Fs.shape[0]; L = lo.shape[0]
    out = np.zeros((P, L), np.uint8)
    for p in nb.prange(P):
        n = sizes[p]; F = Fs[p]; G = Gs[p]
        assign = np.zeros(8, np.int64)
        for l in range(L):
            v = nv[l]; total = n ** v; ok = 1
            for c in range(total):
                r = c
                for i in range(v): assign[i] = r % n; r //= n
                if run(prog, lo[l], mid[l], assign, F, G) != run(prog, mid[l], hi[l], assign, F, G):
                    ok = 0; break
            out[p, l] = ok
    return out

if __name__ == '__main__':
    t0 = time.time()
    laws = list(enumerate_laws(4, ('f', 'g')).values())
    laws.insert(0, (('v', 0), ('v', 0)))  # x = x
    prog, lo, mid, hi, nv = [], [], [], [], []
    for L, R in laws:
        lo.append(len(prog)); postfix(L, prog); mid.append(len(prog)); postfix(R, prog); hi.append(len(prog))
        nv.append(max(nvars(L), nvars(R)))
    probes = build(); P = len(probes)
    Fs = np.zeros((P, NMAX, NMAX), np.int64); Gs = np.zeros_like(Fs); sizes = np.zeros(P, np.int64)
    for i, (_, n, F, G) in enumerate(probes): Fs[i, :n, :n] = F; Gs[i, :n, :n] = G; sizes[i] = n
    print('laws', len(laws), 'probes', P, f'{time.time()-t0:.1f}s setup', flush=True)
    M = evaluate(np.array(prog, np.int64), np.array(lo), np.array(mid), np.array(hi), np.array(nv), Fs, Gs, sizes)
    print(f'matrix done {time.time()-t0:.1f}s, density {M.mean():.4f}', flush=True)
    np.save('M_probe_major.npy', np.packbits(M, axis=1))      # rows = probes, bits = laws
    np.save('M_law_major.npy', np.packbits(M.T, axis=1))      # rows = laws, bits = probes
    meta = {'laws': [render(L) + ' = ' + render(R) for L, R in laws],
            'law_trees': laws, 'order': [len(prog[a:b]) for a, b in zip(lo, hi)],
            'probes': [(name, n) for name, n, _, _ in probes]}
    meta['order'] = [sum(1 for t in prog[a:b] if t >= 10) for a, b in zip(lo, hi)]
    pickle.dump(meta, open('meta.pkl', 'wb'))
    print('saved', f'{time.time()-t0:.1f}s')
