"""T3 analysis: Fisher's exact test for 'has a duality' (named vs random) and percentiles of each named
theory among random theories of the same size.  python -m soup.calib_report [file]"""
import json
import sys
from math import comb

import numpy as np

from .paths import data


def fisher_greater(a, b, c, d):
    """One-sided Fisher exact p-value for the 2x2 table [[a, b], [c, d]]: P(X >= a), hypergeometric."""
    n1, n2, k = a + b, c + d, a + c
    tot = comb(n1 + n2, k)
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot


def pct(x, xs):
    xs = np.asarray(xs, float)
    return round(100 * ((xs < x).mean() + 0.5 * (xs == x).mean()), 1) if len(xs) else None


def e_steps_max(r):
    return max([c.get('e_steps') or 0 for c in r.get('claims', []) if c['status'] == 'proved'] or [0])


def main():
    R = json.load(open(sys.argv[1] if len(sys.argv) > 1 else data('calib_t3.json')))
    named = [r for r in R if r['kind'] == 'named']; null = [r for r in R if r['kind'] == 'null']
    a = sum(bool(r['dualities']) for r in named); b = len(named) - a
    c = sum(bool(r['dualities']) for r in null); d = len(null) - c
    print(f'named {len(named)}, random {len(null)}')
    print(f'has a duality: named {a}/{len(named)}, random {c}/{len(null)}; Fisher one-sided p = {fisher_greater(a, b, c, d):.3g}')
    for k in sorted({len(r['T']) for r in null}):
        nk = [r for r in null if len(r['T']) == k]
        print(f'  random k={k}: n={len(nk)}, with a duality {sum(bool(r["dualities"]) for r in nk)}, '
              f'positive score {sum(r.get("score", 0) > 0 for r in nk)}')
    cols = [('gain', lambda r: r.get('gain', 0)), ('max_difficulty', lambda r: r.get('max_difficulty', 0)),
            ('E steps (max)', e_steps_max), ('richness', lambda r: r.get('richness', 0)), ('score', lambda r: r.get('score', 0))]
    print('\n| theory | k | ' + ' | '.join(f'{n} (pct)' for n, _ in cols) + ' | dualities |')
    print('|---|---|' + '---|' * len(cols) + '---|')
    for r in named:
        nk = [x for x in null if len(x['T']) == len(r['T'])]
        cells = [f'{f(r):.3g} ({pct(f(r), [f(x) for x in nk])})' for _, f in cols]
        print(f"| {r['name']} | {len(r['T'])} | " + ' | '.join(cells) + f" | {','.join(r['dualities']) or '-'} |")


if __name__ == '__main__':
    main()
