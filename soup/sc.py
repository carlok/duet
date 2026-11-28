"""Review item C4 (PREREGISTRATION.md, "Review items B1, B3, C3, C4"; post hoc, 28 Nov 2026): the single-cell
hypothesis SC, a syntactic classification.

    python -m soup.sc [--set n1|n2]     -> check/sc_<set>.json and a summary

SC for the operation `op` (∘ given ·, or · given ∘): op occurs only in subterms u op v with u and v free of op, and every
law is either
  - free of op, or
  - a constraint: its op-subterms are all the same pair (u, v), or the swapped pair (v, u) when T proves op commutative,
  - a tie: exactly u op v = u' op v'.
Under SC (lemma, C4), for a fixed other operation the models form a product over the tie classes of cells; without
ties, over single cells. Commutativity of op is taken from T's axioms or its proved claims (verifier results), then E
(30 s) when a swapped pair needs it.
"""
import argparse
import json

from .paths import data

COMM = {'g': 'x∘y=y∘x', 'f': 'x·y=y·x'}


def has(t, op): return t[0] != 'v' and (t[0] == op or has(t[1], op) or has(t[2], op))


def subterms(t, op):
    """The op-subterms of t as (u, v) pairs, outermost first; None if some has op inside its arguments."""
    if t[0] == 'v': return []
    if t[0] == op:
        if has(t[1], op) or has(t[2], op): return None
        return [(t[1], t[2])]
    a, b = subterms(t[1], op), subterms(t[2], op)
    return None if a is None or b is None else a + b


def law_kind(L, R, op):
    """'free', 'constraint', 'constraint-swap' (needs commutativity), 'tie' or 'bad'."""
    if not has(L, op) and not has(R, op): return 'free'
    if L[0] == op and R[0] == op:
        sL, sR = subterms(L, op), subterms(R, op)
        if sL is not None and sR is not None: return 'tie'
    s = (subterms(L, op) or []) if subterms(L, op) is not None else None
    r = (subterms(R, op) or []) if subterms(R, op) is not None else None
    if s is None or r is None: return 'bad'
    pairs = s + r
    first = pairs[0]
    if all(p == first for p in pairs): return 'constraint'
    if all(p == first or p == (first[1], first[0]) for p in pairs): return 'constraint-swap'
    return 'bad'


def classify(T, op, comm):
    """'SC', 'SC+ties' or 'neither' for op given the other operation; comm: does T prove op commutative?"""
    from .data import TREES
    kinds = [law_kind(*TREES[t], op) for t in T]
    if 'bad' in kinds or ('constraint-swap' in kinds and not comm): return 'neither'
    return 'SC+ties' if 'tie' in kinds else 'SC'


def proves_comm(T, op, res):
    from .named import law_index
    from .provers import prove_e
    g = law_index(COMM[op])
    if g in T: return True
    if res and any(c.get('idx') == g and c.get('status') == 'proved' for c in res.get('claims', [])): return True
    return prove_e(sorted(T), g, processed_limit=500_000, cpu_limit=30)['status'] == 'proved'


def needs_comm(T, op):
    from .data import TREES
    return any(law_kind(*TREES[t], op) == 'constraint-swap' for t in T)


def run(rows):
    import os
    out = []
    for r in rows:
        p = data(r['source'], 'results', f"{r['key']}.json") if r['source'] != '.' else data('results', f"{r['key']}.json")
        res = json.load(open(p)) if os.path.exists(p) else None
        rec = {'key': r['key'], 'source': r['source']}
        for op, name in (('g', 'circ_given_dot'), ('f', 'dot_given_circ')):
            comm = proves_comm(r['T'], op, res) if needs_comm(r['T'], op) else False
            rec[name] = classify(r['T'], op, comm)
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='n1', choices=['n1', 'n2'])
    a = ap.parse_args()
    src = 'novelty_ranking.json' if a.set == 'n1' else 'novelty2_ranking.json'
    rows = json.load(open(data('check', src)))['ranked']
    out = run(rows)
    json.dump(out, open(data('check', f'sc_{a.set}.json'), 'w'), indent=1)
    from collections import Counter
    for name in ('circ_given_dot', 'dot_given_circ'):
        print(name, dict(Counter(r[name] for r in out)))
    both = Counter((r['circ_given_dot'] != 'neither', r['dot_given_circ'] != 'neither') for r in out)
    print(f'{len(out)} theories; SC in at least one direction: {sum(v for k, v in both.items() if any(k))}; '
          f'in both: {both.get((True, True), 0)}')
    # the hypothesis: the five theories studied by hand where ∘ is a constrained choice (ranked or not)
    cands = json.load(open(data('check', 'candidates.json')))
    hyp = [c for c in cands if c['key'][:8] in ('1f430506', '1238c063', '3818b88f', 'de0c0cf3', '71fd2cc6')]
    H = run(hyp)
    json.dump(H, open(data('check', 'sc_hypothesis.json'), 'w'), indent=1)
    for r in H: print(f"  {r['key'][:8]}: ∘ given · {r['circ_given_dot']}, · given ∘ {r['dot_given_circ']}")


if __name__ == '__main__':
    main()
