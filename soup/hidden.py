"""Is one operation a term in the other, as a consequence of the laws? A 'hidden' definitional theory.

    python -m soup.hidden --set candidates        -> SOUP_DATA/check/hidden_candidates.json and a table
    python -m soup.hidden --laws "law; law; ..."
    python -m soup.hidden --param --set candidates [--source x5]   -> check/hidden_param_candidates.json

The search filters definitional theories syntactically (a law x∘y = t with t in · alone, or the converse). A theory
can still imply such a law. Then ∘ is a term in ·, and the theory is a one-operation theory with a defined second
operation, not a fusion of two theories.

Check: binary terms in one operation alone (size <= 5) are evaluated on all models of sizes 2-4 (Mace4, as in
soup.profile). A term that agrees with the other operation on every model is a candidate. E then proves
x∘y = t (or x·y = t) from the laws (30 s, 500,000 processed clauses). Only a proof counts. Added on 22 Nov 2026 as
part of the equivalence check rule 4 asks for; it is not part of the preregistered T5a ranking.
"""
import argparse
import json

from .paths import data, ensure
from .profile import all_models, _positions, term_str, _tptp_sub


def one_op_terms(pos, op, max_size=5, cap=5000):
    X, base, size, Ft, Gt = pos
    tab = Ft if op == 'f' else Gt
    levels = [[(('v', j), X[j]) for j in range(2)]]
    seen = {X[j].tobytes() for j in range(2)}
    for s in range(1, max_size + 1):
        new = []
        for i in range(s):
            for ta, va in levels[i]:
                for tb, vb in levels[s - 1 - i]:
                    v = tab[base + va * size + vb]; k = v.tobytes()
                    if k not in seen: seen.add(k); new.append(((op, ta, tb), v))
        levels.append(new)
        if len(seen) > cap: break
    return [x for lv in levels for x in lv]


def hidden(T, sizes=(2, 3, 4), max_size=5, per_op=3, secs=30):
    from .data import fof
    from .provers import prove_e
    models = [m for n in sizes for m in all_models(T, n, 3000, 60)[0]]
    if not models: return {'models': 0, 'matches': [], 'definitional': None}
    pos = _positions(models, 2)
    X, base, size, Ft, Gt = pos
    axioms = '\n'.join(fof(a, f'a{k}', 'axiom') for k, a in enumerate(T))
    out = []
    for target, other in (('g', 'f'), ('f', 'g')):          # is ∘ a ·-term?  is · a ∘-term?
        tv = (Gt if target == 'g' else Ft)[base + X[0] * size + X[1]]
        hits = [t for t, v in one_op_terms(pos, other, max_size) if (v == tv).all()][:per_op]
        for t in hits:
            src = axioms + f"\nfof(goal,conjecture,! [X,Y] : ({target}(X,Y) = {_tptp_sub(t, (0, 1))})).\n"
            r = prove_e(T, src, processed_limit=500_000, cpu_limit=secs)
            out.append({'op': '∘' if target == 'g' else '·', 'term': term_str(t, 'xy'), 'e': r['status'],
                        'e_steps': r.get('proof_steps')})
            if r['status'] == 'proved': break
    return {'models': len(models), 'matches': out, 'definitional': any(m['e'] == 'proved' for m in out)}


def param_terms(pos, op, max_size=4, cap=2000):
    """Terms in one operation over x, y and the two squares z·z, z∘z (positions of arity 3, z = X[2]). A term that
    uses a square of z stands for a term with a parameter when that square is constant (X5's Steiner loops)."""
    X, base, size, Ft, Gt = pos
    tab = Ft if op == 'f' else Gt
    leaves = [(('v', 0), X[0]), (('v', 1), X[1]),
              (('c', 'f'), Ft[base + X[2] * size + X[2]]), (('c', 'g'), Gt[base + X[2] * size + X[2]])]
    levels, seen = [[]], {}                  # value vector -> the terms that give it (the first, then up to 5 more)
    for t, v in leaves:
        k = v.tobytes()
        if k not in seen: seen[k] = [t]; levels[0].append((t, v))
        elif len(seen[k]) < 6: seen[k].append(t)
    for s in range(1, max_size + 1):
        new = []
        for i in range(s):
            for ta, va in levels[i]:
                for tb, vb in levels[s - 1 - i]:
                    v = tab[base + va * size + vb]; k = v.tobytes()
                    if k not in seen: seen[k] = [(op, ta, tb)]; new.append(((op, ta, tb), v))
                    elif len(seen[k]) < 6: seen[k].append((op, ta, tb))
        levels.append(new)
        if len(seen) > cap: break
    # terms that agree on every model are merged; the alternatives are kept, since E may prove only one of them
    return [(t, v, seen[v.tobytes()]) for lv in levels for t, v in lv]


def _has_const(t): return t[0] == 'c' or (t[0] in 'fg' and (_has_const(t[1]) or _has_const(t[2])))
def _pstr(t): return ('xy'[t[1]] if t[0] == 'v' else ('z·z' if t[1] == 'f' else 'z∘z') if t[0] == 'c'
                      else f"({_pstr(t[1])} {'·' if t[0] == 'f' else '∘'} {_pstr(t[2])})")
def _ptptp(t): return ('XY'[t[1]] if t[0] == 'v' else f'{t[1]}(Z,Z)' if t[0] == 'c'
                       else f'{t[0]}({_ptptp(t[1])},{_ptptp(t[2])})')


def hidden_param(T, models=None, sizes=(2, 3, 4), max_size=4, per_op=3, secs=30, cap_models=300):
    """Is one operation a term in the other plus a constant square (x∘y = t(x, y, z·z or z∘z) for all z)?
    Models: given (the verifier's census) or from Mace4 on sizes 2-4, at most cap_models per size. Only an E proof of
    ![X,Y,Z]: g(X,Y) = t counts (or the same for f). Added 23 Nov 2026 after X5 (ledger row 12)."""
    from .data import fof
    from .provers import prove_e
    if models is None:
        models = [m for n in sizes for m in all_models(T, n, cap_models, 60)[0]]
    if not models: return {'models': 0, 'matches': [], 'definitional': None}
    pos = _positions(models, 3)
    X, base, size, Ft, Gt = pos
    axioms = '\n'.join(fof(a, f'a{k}', 'axiom') for k, a in enumerate(T))
    out = []
    for target, other in (('g', 'f'), ('f', 'g')):
        tv = (Gt if target == 'g' else Ft)[base + X[0] * size + X[1]]
        hits = [u for t, v, alts in param_terms(pos, other, max_size) if (v == tv).all() for u in alts if _has_const(u)]
        for t in hits[:2 * per_op]:
            src = axioms + f"\nfof(goal,conjecture,! [X,Y,Z] : ({target}(X,Y) = {_ptptp(t)})).\n"
            r = prove_e(T, src, processed_limit=500_000, cpu_limit=secs)
            out.append({'op': '∘' if target == 'g' else '·', 'term': _pstr(t), 'e': r['status']})
            if r['status'] == 'proved': break
    return {'models': len(models), 'matches': out, 'definitional': any(m['e'] == 'proved' for m in out)}


def main():
    from .named import law_index
    ap = argparse.ArgumentParser()
    ap.add_argument('--set'); ap.add_argument('--laws')
    ap.add_argument('--param', action='store_true', help='definitions with a constant square (hidden_param)')
    ap.add_argument('--source', help='with --set candidates: only this source')
    a = ap.parse_args()
    if a.set == 'candidates':
        jobs = [(str(r['key']), r['source'], r['laws'], r['T']) for r in json.load(open(data('check', 'candidates.json')))]
    else:
        laws = [s.strip() for s in a.laws.split(';')]
        jobs = [('adhoc', 'cli', laws, [law_index(s.replace(' ', '')) for s in laws])]
    if a.source: jobs = [j for j in jobs if j[1] == a.source]
    out = ensure('check') / f"hidden{'_param' if a.param else ''}_{a.set}.json" if a.set else None
    res = json.load(open(out)) if out and out.exists() else []           # resumable: theories already checked are kept
    done = {json.dumps(sorted(r['T'])) for r in res}
    for key, src, laws, T in jobs:
        if json.dumps(sorted(T)) in done: continue
        h = (hidden_param if a.param else hidden)(T); res.append(dict(h, key=key, source=src, laws=laws, T=T))
        m = '; '.join(f"{x['op']} = {x['term']} ({x['e']})" for x in h['matches']) or '-'
        print(f"{key[:8]:8s} {src:10s} models {h['models']:4d} definitional {h['definitional']} | {m}", flush=True)
        if out: json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
