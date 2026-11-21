"""Machine check of an offline LLM bundle (prompts/README.md). Nothing in the bundle is trusted or run.

    tar -C ~/tmp/duet-offline/<bundle> -cf - . | podman run -i --rm -v "$PWD/work:/data:ro" soup \
        python -m soup.check_offline > ~/tmp/duet-offline/<bundle>/check.jsonl

The bundle arrives as a tar on stdin, so no container mounts the offline directory. Only the per-theory
files `S<n>.md` are read; each starts with `# S<n> (`<key>`)`. Axioms and open claims come from our
`results/<key>*.json`, never from the bundle text. What is taken from the bundle:
  - finite models: the Cayley tables ("As nested lists (row-major)"); checked with core.law_vector and by
    direct evaluation of data.TREES: every axiom holds, every open claim fails, both operations essentially
    binary and distinct;
  - models on Z: transcribed here by hand from the bundle (ZMODELS, with a marker string that must appear in
    the file); each axiom is proved for all integers by z3 (linear integer arithmetic, negation unsat),
    each claim is evaluated at 0;
  - the S7 term model: reimplemented here from its prose definition (TERM_MODELS), not from the bundle's
    code; axioms and claim are tested on generated elements. This is a sample, not a certificate;
  - lemma chains ("E1. ... = ..."): each lemma is proved from the theory's axioms by E. A proved lemma is a
    consequence of the axioms whoever proposed it.
Output: one JSON line per item on stdout. Results go to REPORT.md only as "found offline with an LLM,
machine-checked", never into work/results, the corpus or the archive.
"""
import ast
import glob
import io
import itertools
import json
import random
import re
import sys
import tarfile

import numpy as np
import z3

from .data import TREES, LAWS, tptp
from .named import parse

# ---- evaluation of our law trees under arbitrary operations

def ev(t, env, f, g):
    if t[0] == 'v': return env[t[1]]
    a, b = ev(t[1], env, f, g), ev(t[2], env, f, g)
    return f(a, b) if t[0] == 'f' else g(a, b)


def nv(t): return t[1] + 1 if t[0] == 'v' else max(nv(t[1]), nv(t[2]))


def law_nvars(i): L, R = TREES[i]; return max(nv(L), nv(R))


def holds_finite(i, F, G):
    n = len(F); L, R = TREES[i]
    f = lambda a, b: F[a][b]; g = lambda a, b: G[a][b]
    return all(ev(L, e, f, g) == ev(R, e, f, g) for e in itertools.product(range(n), repeat=law_nvars(i)))


def check_finite(T, claims, F, G):
    from .core import law_vector, is_nondeg
    n = len(F)
    ok_shape = all(len(r) == n and all(isinstance(v, int) and 0 <= v < n for v in r) for r in F + G) and len(G) == n
    if not ok_shape: return {'ok': False, 'why': 'tables malformed'}
    lv = law_vector(np.array(F), np.array(G), n)
    ax = {LAWS[t]: holds_finite(t, F, G) for t in T}
    cl = {LAWS[c]: not holds_finite(c, F, G) for c in claims}
    agree = all(lv[t] == ax[LAWS[t]] for t in T) and all((not lv[c]) == cl[LAWS[c]] for c in claims)
    return {'ok': all(ax.values()) and all(cl.values()) and agree, 'n': n, 'axioms_hold': ax, 'claims_fail': cl,
            'law_vector_agrees': agree, 'nondeg': bool(is_nondeg(np.array(F), np.array(G), n))}


# ---- models on Z, transcribed by hand from the bundle (marker: a string that must occur in the file)

def _max(a, b): return z3.If(a >= b, a, b)
def _min(a, b): return z3.If(a <= b, a, b)


ZMODELS = {
    '00f017a6': {'marker': 'x · y = 2y − x − 1   if x ≥ y',              # S1
                 'f': lambda x, y: z3.If(x < y, x, 2 * y - x - 1), 'g': lambda x, y: z3.If(y < x, x, 2 * y - x + 1)},
    'e6403d7a': {'marker': 'x ∘ y = 2x − y + 1   if x ≥ y',              # S9
                 'f': lambda x, y: z3.If(x < y, x, 2 * y - x - 1), 'g': lambda x, y: z3.If(x < y, y, 2 * x - y + 1)},
    'f5321de4': {'marker': 'x · y = max(x, y)   if x ≠ y,      x · x = x + 1',   # S11
                 'f': lambda x, y: z3.If(x != y, _max(x, y), x + 1), 'g': lambda x, y: z3.If(x != y, _min(x, y), x - 1)},
}


def prove_over_Z(i, f, g):
    """True iff law i holds for all integers under (f, g): z3 shows its negation unsatisfiable."""
    L, R = TREES[i]; k = law_nvars(i)
    vs = [z3.Int(f'v{j}') for j in range(k)]
    s = z3.Solver(); s.set('timeout', 60_000)
    s.add(ev(L, vs, f, g) != ev(R, vs, f, g))
    r = s.check()
    return 'proved' if r == z3.unsat else 'counterexample' if r == z3.sat else 'unknown'


def check_Z(T, claims, m):
    ax = {LAWS[t]: prove_over_Z(t, m['f'], m['g']) for t in T}
    cl = {}
    for c in claims:
        L, R = TREES[c]; zero = [z3.IntVal(0)] * law_nvars(c)
        a, b = z3.simplify(ev(L, zero, m['f'], m['g'])), z3.simplify(ev(R, zero, m['f'], m['g']))
        cl[LAWS[c]] = {'fails_at_0': a.as_long() != b.as_long(), 'values': [a.as_long(), b.as_long()]}
    ok = all(v == 'proved' for v in ax.values()) and all(v['fails_at_0'] for v in cl.values())
    return {'ok': ok, 'axioms_over_Z': ax, 'claims': cl}


# ---- the S7 term model, reimplemented from the prose of S7.md (generators are strings,
#      ('C', u, v) is the formal circle term [u∘v], ('P', u, v) the formal dot term [u·v])

def _alpha(t, memo={}):
    if t in memo: return memo[t]
    if isinstance(t, str) or t[0] == 'P': r = t
    else:
        _, u, v = t
        if not isinstance(v, str) and v[0] == 'P' and v[1] == u: r = _alpha(v[2])          # case (a)
        elif not isinstance(u, str) and u[0] == 'C' and v == u[1]: r = _alpha(u[1])      # case (b)
        else: r = t                                                                     # case (c)
    memo[t] = r; return r


def s7_circ(u, v): return u if u == v else ('C', u, v)


def s7_dot(u, v):
    if _alpha(u) == _alpha(v): return u                                                 # rule 1
    if not isinstance(u, str) and u[0] == 'C' and _alpha(u[1]) == _alpha(v): return u[1]   # rule 2
    return ('P', u, v)                                                                  # rule 3


def check_s7(T, claims, n_elems=500, n_triples=200_000, seed=1):
    rng = random.Random(seed)
    E = ['x', 'y', 'z']
    for _ in range(2):
        E = list(dict.fromkeys(E + [op(a, b) for a in E for b in E for op in (s7_dot, s7_circ)]))
    while len(E) < n_elems:
        a, b = rng.choice(E), rng.choice(E); E.append(rng.choice((s7_dot, s7_circ))(a, b))
    E = list(dict.fromkeys(E))
    fails = {}
    for t in T:
        L, R = TREES[t]; k = law_nvars(t); bad = 0
        envs = itertools.product(E[:60], repeat=k) if k <= 2 else (tuple(rng.choice(E) for _ in range(k)) for _ in range(n_triples))
        for e in envs:
            if ev(L, e, s7_dot, s7_circ) != ev(R, e, s7_dot, s7_circ): bad += 1
        fails[LAWS[t]] = bad
    cl = {}
    for c in claims:
        L, R = TREES[c]; e = ('x', 'y', 'z')[:law_nvars(c)]
        cl[LAWS[c]] = ev(L, e, s7_dot, s7_circ) != ev(R, e, s7_dot, s7_circ)
    return {'ok': all(v == 0 for v in fails.values()) and all(cl.values()), 'elements': len(E),
            'axiom_failures': fails, 'claims_fail_at_generators': cl, 'kind': 'sampled, not certified'}


TERM_MODELS = {'cdf702b5': check_s7}


# ---- lemmas: proved from the axioms by E

LEMMA_TICK = re.compile(r'^\s*-?\s*([EF]\d+)\.\s+`([^`\n]+=[^`\n]+)`', re.M)      # "- E1. `lhs = rhs`. why"
LEMMA_LINE = re.compile(r'^\s*([EF]\d+)\.\s+([^`\n:]+=[^`\n:]+)$', re.M)            # "E1. lhs = rhs" (code block)


def lemmas(body):
    found = sorted(((m.start(), m.group(1), m.group(2)) for p in (LEMMA_TICK, LEMMA_LINE) for m in p.finditer(body)))
    out, seen = [], set()
    for _, name, eq in found:
        if name in seen: continue
        seen.add(name)
        eq = eq.strip().rstrip('.')
        try:
            l, r = eq.split('=')
            out.append((name, eq, parse(l), parse(r)))
        except Exception:
            out.append((name, eq, None, None))
    return out


def _vars(t): return {t[1]} if t[0] == 'v' else _vars(t[1]) | _vars(t[2])


def lemma_problem(T, L, R, extra=()):
    from .data import fof
    vs = sorted({'XYZWUV'[v] for v in _vars(L) | _vars(R)})
    goal = f"fof(goal,conjecture,{('! [' + ','.join(vs) + '] : ') if vs else ''}({tptp(L)} = {tptp(R)}))."
    ax = [fof(t, f'a{k}', 'axiom') for k, t in enumerate(T)]
    return '\n'.join(ax + list(extra) + [goal]) + '\n'


def check_lemmas(T, body):
    from .provers import prove_e
    res = []
    for name, eq, L, R in lemmas(body):
        if L is None: res.append({'lemma': name, 'eq': eq, 'status': 'unparsed'}); continue
        r = prove_e(T, lemma_problem(T, L, R), processed_limit=200_000, cpu_limit=60)
        res.append({'lemma': name, 'eq': eq, 'status': r['status'], 'e_steps': r.get('proof_steps')})
    return res


# ---- driver

HEAD = re.compile(r'^# (S\d+) \(`([0-9a-f]+)`\)', re.M)
TABLES = re.compile(r'As nested lists \(row-major\): `(\[\[.*?\]\])`')


def our_result(key):
    from .paths import data
    fs = glob.glob(str(data('results', f'{key}*.json')))
    return json.load(open(fs[0])) if len(fs) == 1 else None


def check_file(name, body, emit):
    m = HEAD.search(body)
    if not m: emit({'file': name, 'ok': False, 'why': 'no header'}); return
    theory, key = m.groups(); r = our_result(key)
    if r is None: emit({'file': name, 'theory': theory, 'key': key, 'ok': False, 'why': 'key not in results'}); return
    T = r['T']; claims = [c['idx'] for c in r['claims'] if c['status'] in ('unknown', 'open')]
    base = {'file': name, 'theory': theory, 'key': key}
    lists = TABLES.findall(body)
    for j in range(0, len(lists) - 1, 2):
        F, G = ast.literal_eval(lists[j]), ast.literal_eval(lists[j + 1])
        emit(dict(base, item='finite model', **check_finite(T, claims, F, G)))
    for k, mdl in ZMODELS.items():
        if key.startswith(k):
            if mdl['marker'] not in body: emit(dict(base, item='Z model', ok=False, why='marker not found')); continue
            emit(dict(base, item='Z model', **check_Z(T, claims, mdl)))
    for k, fn in TERM_MODELS.items():
        if key.startswith(k): emit(dict(base, item='term model', **fn(T, claims)))
    for x in check_lemmas(T, body):
        emit(dict(base, item='lemma', ok=x['status'] == 'proved', **x))


def main():
    emit = lambda d: print(json.dumps(d, ensure_ascii=False, default=str), flush=True)
    with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()), mode='r:*') as tf:
        files = {m.name.split('/')[-1]: m for m in tf.getmembers() if m.isfile()}
        for fname in sorted((f for f in files if re.fullmatch(r'S\d+\.md', f)), key=lambda f: int(f[1:-3])):
            body = tf.extractfile(files[fname]).read().decode('utf-8')
            check_file(fname, body, emit)


if __name__ == '__main__':
    main()
