"""Independent check of an E saturation ('CounterSatisfiable') for a unit equational problem.

Given E's saturated clause set S (--print-saturated), check in plain Python:
  1. every equation of S orients as a rewrite rule l -> r with |l| > |r| and vars(r) <= vars(l)
     (size-decreasing, hence terminating; a saturation with unorientable equations is not handled),
  2. every critical pair of the rule set is joinable (so R is confluent, Knuth-Bendix),
  3. every input axiom is joinable in R,
  4. the two sides of the goal, with its variables as fresh constants, have different normal forms.
Then the term algebra modulo R (normal forms, goal variables as free constants) is a model of the axioms
(3, joinability is closed under substitution) in which the goal fails (4): the goal is not a consequence
of the axioms. Whether E derived R soundly does not matter: the argument only needs 1-4, all checked here,
so E is only the search heuristic that proposes R.
"""
from collections import Counter
import itertools
import re
import subprocess
import sys

from .provers import problem, E_BIN, PROVER_MB

# terms: ('v', name) | (fname, (args...))


def parse_term(s, i=0):
    m = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)', s[i:]); name = m.group(1); i += m.end()
    if i < len(s) and s[i] == '(':
        args = []; i += 1
        while True:
            t, i = parse_term(s, i); args.append(t)
            while s[i] == ' ': i += 1
            if s[i] == ',': i += 1; continue
            if s[i] == ')': i += 1; break
        return (name, tuple(args)), i
    return (('v', name) if name[0].isupper() else (name, ())), i


def size(t): return 1 if t[0] == 'v' else 1 + sum(size(a) for a in t[1])
def occ(t): return Counter([t[1]]) if t[0] == 'v' else sum((occ(a) for a in t[1]), Counter())
def tvars(t): return {t[1]} if t[0] == 'v' else set().union(*[tvars(a) for a in t[1]]) if t[1] else set()


def subst(t, s):
    if t[0] == 'v': return s.get(t[1], t)
    return (t[0], tuple(subst(a, s) for a in t[1]))


def match(p, t, s):
    if p[0] == 'v':
        if p[1] in s: return s if s[p[1]] == t else None
        s = dict(s); s[p[1]] = t; return s
    if t[0] == 'v' or p[0] != t[0] or len(p[1]) != len(t[1]): return None
    for a, b in zip(p[1], t[1]):
        s = match(a, b, s)
        if s is None: return None
    return s


def unify(a, b, s=None):
    s = dict(s or {})
    def walk(t):
        while t[0] == 'v' and t[1] in s: t = s[t[1]]
        return t
    def occurs(v, t):
        t = walk(t)
        return t[1] == v if t[0] == 'v' else any(occurs(v, x) for x in t[1])
    stack = [(a, b)]
    while stack:
        x, y = stack.pop(); x, y = walk(x), walk(y)
        if x == y: continue
        if x[0] == 'v':
            if occurs(x[1], y): return None
            s[x[1]] = y
        elif y[0] == 'v':
            if occurs(y[1], x): return None
            s[y[1]] = x
        elif x[0] != y[0] or len(x[1]) != len(y[1]): return None
        else: stack.extend(zip(x[1], y[1]))
    def full(t):
        t = walk(t)
        return t if t[0] == 'v' else (t[0], tuple(full(u) for u in t[1]))
    return {v: full(t) for v, t in s.items()}


def normal(t, R):
    if t[0] != 'v': t = (t[0], tuple(normal(a, R) for a in t[1]))
    for l, r in R:
        s = match(l, t, {})
        if s is not None: return normal(subst(r, s), R)
    return t


def positions(t, p=()):
    yield p, t
    if t[0] != 'v':
        for i, a in enumerate(t[1]): yield from positions(a, p + (i,))


def replace(t, p, u):
    if not p: return u
    args = list(t[1]); args[p[0]] = replace(args[p[0]], p[1:], u); return (t[0], tuple(args))


def rename(t, suf): return ('v', t[1] + suf) if t[0] == 'v' else (t[0], tuple(rename(a, suf) for a in t[1]))


def critical_pairs(R):
    for (l1, r1), (l2, r2) in itertools.product(R, R):
        l2, r2 = rename(l2, "'"), rename(r2, "'")
        for p, sub in positions(l1):
            if sub[0] == 'v': continue
            s = unify(sub, l2)
            if s is None: continue
            if p == () and (l1, r1) == (rename(l2, ''), r2): pass
            yield subst(r1, s), subst(replace(l1, p, r2), s)


def check(T, goal, cpu=60):
    src = problem(T, goal)
    try:
        out = subprocess.run([E_BIN, '--auto', '-s', '--print-saturated', f'--cpu-limit={cpu}',
                              f'--memory-limit={PROVER_MB}'], input=src, capture_output=True, text=True,
                             timeout=cpu + 30).stdout
    except subprocess.TimeoutExpired:
        return {'ok': False, 'why': 'E wall timeout'}
    if 'CounterSatisfiable' not in out: return {'ok': False, 'why': 'E did not saturate'}
    R = []
    for line in out.splitlines():
        m = re.match(r'cnf\(\w+, plain, \((.*)\)\)\.$', line.strip())
        if not m: continue
        body = m.group(1)
        if '!=' in body: continue
        l, i = parse_term(body); assert body[i] == '='; r, _ = parse_term(body, i + 1)
        if size(l) < size(r): l, r = r, l
        if not (size(l) > size(r) and all(occ(l)[v] >= k for v, k in occ(r).items())):
            return {'ok': False, 'why': f'unorientable by size: {body}'}
        R.append((l, r))
    cps = list(critical_pairs(R))
    bad = [(a, b) for a, b in cps if normal(a, R) != normal(b, R)]
    if bad: return {'ok': False, 'why': f'{len(bad)} non-joinable critical pairs', 'rules': len(R)}
    ax = []
    for line in src.splitlines():
        m = re.match(r'fof\((\w+),(axiom|conjecture),(?:! \[[^\]]*\] : )?\((.*)\)\)\.$', line)
        l, i = parse_term(m.group(3)); r, _ = parse_term(m.group(3), i + 3)
        ax.append((m.group(2), l, r))
    for role, l, r in ax:
        if role == 'axiom' and normal(l, R) != normal(r, R): return {'ok': False, 'why': 'axiom not joinable'}
    _, gl, gr = [a for a in ax if a[0] == 'conjecture'][0]
    sk = {v: (f'sk_{v.lower()}', ()) for v in tvars(gl) | tvars(gr)}
    nl, nr = normal(subst(gl, sk), R), normal(subst(gr, sk), R)
    return {'ok': nl != nr, 'rules': len(R), 'critical_pairs': len(cps), 'goal_normal_forms': [repr(nl), repr(nr)]}


if __name__ == '__main__':
    import json
    from .t2_smoke import CASES
    from .named import law_index
    out = {}
    for name in ['A => x·x=x', 'B => x·x=x', 'C => x·x=x', 'D => x·x=x']:
        T, g = CASES[name]; out[name] = check(T, law_index(g))
        print(name, json.dumps(out[name]), flush=True)
