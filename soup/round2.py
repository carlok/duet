"""Second survivor round: the claims of S12 (f5e53602) and S10 (f096b282) that the offline LLM left open.

    python -m soup.round2 clean [--jobs 5] [--secs 3600]          > results in SOUP_DATA/check/round2_clean.json
    tar -C <bundle> -cf - S10.md S12.md | python -m soup.round2 assisted [--jobs N]   > JSON lines on stdout

Claims (dual claims are skipped: S12 is closed under swapping the operations, so x o x = x is the dual of
x.x = x; in S10, x.x = x and x o x = x are equivalent through the axiom x.x = x o x):
  S12 x.x = x, S12 x.x = x o x, S10 x.x = x, S10 x.(x.x) = x.
clean     no input from the LLM: E --auto-schedule, Vampire casc and casc_sat, Twee, Prover9 (secs each);
          Mace4 (S12 from size 6, S10 from 7, to 9; 2*secs); cyclic models on Z/n, n <= 64; piecewise-linear
          models on Z with window 3.
assisted  the LLM's lemmas (S12 E1-E13, S10 F1-F2 plus the S12 lemmas, which hold in S10), each first proved
          from the axioms by E, added as axioms for E, Vampire and Twee; the one-operation specialisation
          x.y = x o y in Mace4 from size 9 to 12. Output is for the offline table only.
Every outcome is re-checked before it is reported: proofs by a second prover, saturations by
soup.confluence, finite models by core.law_vector, Z-models by the proof over Z inside families.
"""
import argparse
import io
import json
import re
import sys
import tarfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from .named import law_index
from .paths import data, ensure

S12, S10 = 'f5e53602', 'f096b282'
CLAIMS = [(S12, 'x · x = x'), (S12, 'x · x = x ∘ x'), (S10, 'x · x = x'), (S10, 'x · (x · x) = x')]


def theory(key):
    import glob
    r = json.load(open(glob.glob(str(data('results', f'{key}*.json')))[0]))
    return r['T']


def goal_idx(s): return law_index(s.replace(' ', ''))


def run(job):
    from . import provers, families
    track, key, claim, tool, arg = job
    T = theory(key); g = goal_idx(claim); t0 = time.time()
    src = arg.get('src') if isinstance(arg, dict) else None
    goal = src if src else g
    if tool == 'e':
        r = provers.prove_e(T, goal, processed_limit=10 ** 9, cpu_limit=arg['secs'], auto='--auto-schedule')
    elif tool in ('vampire_casc', 'vampire_casc_sat'):
        r = provers.prove_vampire(T, goal, cpu_limit=arg['secs'], extra=('--mode', tool[len('vampire_'):]))
    elif tool == 'twee':
        r = provers.prove_twee(T, goal, seconds=arg['secs'])
    elif tool == 'prover9':
        r = provers.prove_prover9(T, g, seconds=arg['secs'], extra_axioms=arg.get('lemmas', ()))
    elif tool == 'mace4':
        TT = arg.get('T', T); gg = arg.get('goal', g)
        r = provers.mace4(TT, gg, arg['lo'], arg['hi'], arg['secs'])
        if r.get('size'):
            import numpy as np
            from .core import law_vector
            F, G = (np.array(x) for x in r['tables'])
            lv = law_vector(F, G, r['size']); r['checked'] = bool(all(lv[t] for t in TT) and not lv[gg])
    elif tool == 'cyclic':
        r = {'status': 'none found', 'n_max': arg['n_max'], 'unknown_n': []}
        for n in range(2, arg['n_max'] + 1):
            m = families.cyclic(T, g, n, timeout_ms=arg['ms'])
            if m == 'unknown': r['unknown_n'].append(n); continue
            if m is not None:
                r = {'status': 'model', 'n': n, 'F': m[0].tolist(), 'G': m[1].tolist(),
                     'checked': families.check_tables(T, g, *m)}; break
    elif tool == 'zpw':
        m = families.z_piecewise(T, g, W=arg['W'], deadline=time.time() + arg['secs'])
        r = {'status': 'model' if isinstance(m, dict) else (m or 'none in family'), 'model': m if isinstance(m, dict) else None}
    else:
        raise ValueError(tool)
    r = {k: v for k, v in r.items() if k != 'proof'} | ({'proof': r['proof'][:20000]} if r.get('proof') else {})
    return {'track': track, 'theory': key, 'claim': claim, 'tool': tool,
            'arg': {k: v for k, v in (arg or {}).items() if k not in ('src', 'lemmas', 'T')}, **r,
            'wall': round(time.time() - t0, 1)}


def clean_jobs(secs):
    js = []
    for key, claim in CLAIMS:                 # order: S12 x.x = x first (it would settle all six)
        for tool in ('twee', 'vampire_casc', 'e', 'vampire_casc_sat', 'prover9'):
            js.append(('clean', key, claim, tool, {'secs': secs}))
        js.append(('clean', key, claim, 'mace4', {'lo': 6 if key == S12 else 7, 'hi': 9, 'secs': 2 * secs}))
        js.append(('clean', key, claim, 'cyclic', {'n_max': 64, 'ms': 300_000}))
        js.append(('clean', key, claim, 'zpw', {'W': 3, 'secs': secs}))
    return js


# ---- assisted track: lemmas from the bundle, each proved by E first

def bundle_lemmas(tar_bytes):
    from .check_offline import lemmas
    out = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:*') as tf:
        for m in tf.getmembers():
            name = m.name.split('/')[-1]
            if name in ('S10.md', 'S12.md'): out[name] = tf.extractfile(m).read().decode()
    return {k: [(n, eq, L, R) for n, eq, L, R in lemmas(v) if L is not None] for k, v in out.items()}


def proved_lemmas(key, ls):
    from .check_offline import lemma_problem
    from .provers import prove_e
    T = theory(key)
    return [(n, L, R) for n, eq, L, R in ls if prove_e(T, lemma_problem(T, L, R), 200_000, 60)['status'] == 'proved']


def lemma_tptp(T, goal, lem):
    from .data import fof, tptp, TREES
    from .check_offline import _vars
    def f(name, role, L, R):
        vs = sorted({'XYZWUV'[v] for v in _vars(L) | _vars(R)})
        return f"fof({name},{role},{('! [' + ','.join(vs) + '] : ') if vs else ''}({tptp(L)} = {tptp(R)}))."
    lines = [fof(t, f'a{k}', 'axiom') for k, t in enumerate(T)] + [f(f'lemma_{n.lower()}', 'axiom', L, R) for n, L, R in lem]
    L, R = TREES[goal]
    return '\n'.join(lines + [f('goal', 'conjecture', L, R)]) + '\n'


def assisted_jobs(secs, tar_bytes):
    ls = bundle_lemmas(tar_bytes)
    s12 = proved_lemmas(S12, ls.get('S12.md', []))
    s10 = proved_lemmas(S10, ls.get('S10.md', [])) + proved_lemmas(S10, ls.get('S12.md', []))
    info = {'S12 lemmas proved': [n for n, *_ in s12], 'S10 lemmas proved': [n for n, *_ in s10]}
    js = []
    for key, claim in CLAIMS[:3]:
        lem = s12 if key == S12 else s10
        src = lemma_tptp(theory(key), goal_idx(claim), lem)
        for tool in ('twee', 'vampire_casc', 'e'):
            js.append(('assisted', key, claim, tool, {'secs': secs, 'src': src, 'n_lemmas': len(lem)}))
    one = [law_index('x = x·(y·(y·(x·y)))'), law_index('y = (((x·y)·x)·x)·y')]
    js.append(('assisted', S12, 'x · x = x', 'mace4', {'lo': 9, 'hi': 12, 'secs': 2 * secs, 'T': one,
                                                       'goal': law_index('x·x = x'), 'one_op': True}))
    return js, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('track', choices=['clean', 'assisted']); ap.add_argument('--jobs', type=int, default=5)
    ap.add_argument('--secs', type=int, default=3600)
    a = ap.parse_args()
    if a.track == 'clean':
        js, info = clean_jobs(a.secs), {}
        out_path = ensure('check') / 'round2_clean.json'
    else:
        js, info = assisted_jobs(a.secs, sys.stdin.buffer.read())
        out_path = None
        print(json.dumps({'info': info}, ensure_ascii=False), flush=True)
    res = []
    with ProcessPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(run, j) for j in js]):
            try: r = f.result()
            except Exception as e: r = {'error': repr(e)}
            res.append(r)
            line = json.dumps({k: v for k, v in r.items() if k not in ('proof', 'F', 'G', 'tables')}, ensure_ascii=False, default=str)
            if out_path:
                json.dump(res, open(out_path, 'w'), ensure_ascii=False, indent=1, default=str)
                print(line, file=sys.stderr, flush=True)
            else:
                print(json.dumps(r, ensure_ascii=False, default=str), flush=True)


if __name__ == '__main__':
    main()
