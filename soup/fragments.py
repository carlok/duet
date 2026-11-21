"""Fragment check (T4 primary outcome): is every law of a verified theory valid in a named theory?

    python -m soup.fragments [glob]     default: SOUP_DATA/results/*.json; *.pkl reads first-session files
                                        env FRAG_JOBS (8), FRAG_ALL=1 to include score <= 0

Validity of a law t in a named theory N (from soup.calib.NAMED, 10 theories):
  invalid    a corpus structure (base or found) satisfying N's axioms violates t, or E saturates on N |- t
             and soup.confluence certifies the saturation;
  valid      E proves N |- t (200k processed clauses), else z3 proves it (rlimit 2M);
  undecided  otherwise.
A theory is a fragment of N if all its laws are valid in N, not a fragment if one is invalid, else undecided.
(The first-session version counted "z3 gave up" as "not a fragment", which biased results toward novelty.)
Output: SOUP_DATA/fragments.json and a summary on stdout.
"""
import glob
import json
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

from .calib import NAMED
from .named import law_index
from .paths import data

AX = {k: sorted(law_index(s) for s in v) for k, v in NAMED.items()}


def _prove_job(job):
    from .confluence import check
    from .core import prove
    from .provers import prove_e
    name, t = job
    e = prove_e(AX[name], t, processed_limit=200_000, cpu_limit=60)
    if e['status'] == 'proved': return name, t, 'valid', 'E'
    if e['status'] == 'countersatisfiable':
        return name, t, ('invalid' if check(AX[name], t).get('ok') else 'undecided'), 'E saturation'
    if prove(AX[name], t, 2_000_000)[0] == 'proved': return name, t, 'valid', 'z3'
    return name, t, 'undecided', 'no proof, no countermodel'


def load(pattern):
    rows = []
    for f in sorted(glob.glob(pattern)):
        if f.endswith('.pkl'):
            for T, r in pickle.load(open(f, 'rb'))['verified'].items():
                rows.append(dict(r, T=sorted(set(T)), key=r.get('key') or ','.join(map(str, sorted(set(T))))))
        else:
            rows.append(json.load(open(f)))
    return rows


def main():
    from .core import Corpus
    pattern = sys.argv[1] if len(sys.argv) > 1 else str(data('results', '*.json'))
    rows = [r for r in load(pattern) if os.environ.get('FRAG_ALL') or (r.get('score') or 0) > 0]
    C = Corpus(store=data('corpus'))
    imp = {n: C.implied(ax) for n, ax in AX.items()}      # laws true in every corpus model of N
    status, how, todo = {}, {}, set()
    for r in rows:
        for t in r['T']:
            for n in AX:
                if (n, t) in status or (n, t) in todo: continue
                if t in AX[n]: status[(n, t)] = 'valid'; how[(n, t)] = 'axiom'
                elif imp[n] is not None and not imp[n][t]: status[(n, t)] = 'invalid'; how[(n, t)] = 'finite model'
                else: todo.add((n, t))
    with ProcessPoolExecutor(int(os.environ.get('FRAG_JOBS', 8))) as ex:
        for f in as_completed([ex.submit(_prove_job, j) for j in sorted(todo)]):
            n, t, st, h = f.result(); status[(n, t)] = st; how[(n, t)] = h
    out = []
    for r in rows:
        per = {}
        for n in AX:
            sts = [status[(n, t)] for t in r['T']]
            per[n] = 'fragment' if all(s == 'valid' for s in sts) else ('not' if 'invalid' in sts else 'undecided')
        out.append({'key': r.get('key'), 'score': r.get('score'), 'arm': r.get('arm'), 'dualities': r.get('dualities', []),
                    'laws': r.get('laws'), 'T': r['T'], 'per_named': per,
                    'fragment_of': [n for n, s in per.items() if s == 'fragment'],
                    'undecided': [n for n, s in per.items() if s == 'undecided']})
    json.dump(out, open(data('fragments.json'), 'w'), ensure_ascii=False, indent=1)
    n_frag = sum(bool(x['fragment_of']) for x in out)
    n_und = sum(not x['fragment_of'] and bool(x['undecided']) for x in out)
    print(f'{len(out)} theories ({pattern}): {n_frag} fragments of a named theory, {n_und} undecided, '
          f'{len(out) - n_frag - n_und} fragments of none')
    for n in AX:
        print(f'  {n}: {sum(x["per_named"][n] == "fragment" for x in out)} fragments, '
              f'{sum(x["per_named"][n] == "undecided" for x in out)} undecided')
    print('law validity checks:', {s: sum(v == s for v in status.values()) for s in ('valid', 'invalid', 'undecided')})
    for x in sorted(out, key=lambda x: -(x['score'] or 0))[:20]:
        print(f"{x['score'] or 0:.3f} {','.join(x['dualities']) or '-':14s} {' & '.join(x['laws'] or [])[:110]}  -> "
              f"{', '.join(x['fragment_of']) or ('undecided: ' + ', '.join(x['undecided']) if x['undecided'] else 'none')}")


if __name__ == '__main__':
    main()
