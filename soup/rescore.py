"""Post-hoc comparison: verified results rescored with V2 difficulty (E proof steps / 10) instead of z3 effort.
Claim selection cannot be redone after the fact, so this changes the difficulty only. Labelled post hoc.
    python -m soup.rescore"""
import copy
import glob
import json

from .paths import data
from .verify import score, set_difficulty, V2


def main():
    rs = [json.load(open(f)) for f in sorted(glob.glob(str(data('results', '*.json'))))]
    new = []
    for r in rs:
        x = copy.deepcopy(r)
        for c in x.get('claims', []):
            if c['status'] == 'proved':
                c.setdefault('difficulty_z3', c.get('difficulty', 0.0)); set_difficulty(c, V2)
        new.append(score(x))
    old_rank = {r['key']: i for i, r in enumerate(sorted(rs, key=lambda r: -(r.get('score') or 0)))}
    print(f'{len(rs)} results; proved claims without E steps (difficulty 0.1): '
          f"{sum(bool(c.get('no_e_proof')) for x in new for c in x.get('claims', []))}")
    print('rank V2 | rank V1 | score V2 | score V1 | laws')
    for i, x in enumerate(sorted(new, key=lambda r: -(r.get('score') or 0))[:15]):
        old = [r for r in rs if r['key'] == x['key']][0]
        print(f"{i + 1} | {old_rank[x['key']] + 1} | {x['score']:.3f} | {old.get('score') or 0:.3f} | {' & '.join(x['laws'])[:110]}")


if __name__ == '__main__':
    main()
