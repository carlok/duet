"""Is one operation a term in the other, as a consequence of the laws? A 'hidden' definitional theory.

    python -m soup.hidden --set candidates        -> SOUP_DATA/check/hidden_candidates.json and a table
    python -m soup.hidden --laws 'law; law; ...'

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


def main():
    from .named import law_index
    ap = argparse.ArgumentParser()
    ap.add_argument('--set'); ap.add_argument('--laws')
    a = ap.parse_args()
    if a.set == 'candidates':
        jobs = [(str(r['key']), r['source'], r['laws'], r['T']) for r in json.load(open(data('check', 'candidates.json')))]
    else:
        laws = [s.strip() for s in a.laws.split(';')]
        jobs = [('adhoc', 'cli', laws, [law_index(s.replace(' ', '')) for s in laws])]
    res = []
    for key, src, laws, T in jobs:
        h = hidden(T); res.append(dict(h, key=key, source=src, laws=laws, T=T))
        m = '; '.join(f"{x['op']} = {x['term']} ({x['e']})" for x in h['matches']) or '-'
        print(f"{key[:8]:8s} {src:10s} models {h['models']:4d} definitional {h['definitional']} | {m}", flush=True)
    if a.set: json.dump(res, open(ensure('check') / f'hidden_{a.set}.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
