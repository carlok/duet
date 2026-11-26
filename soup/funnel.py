"""The funnel over all runs, from cheap evaluations to the candidates studied closely (23 Nov 2026).

    podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes" -v "$PWD/README.md:/repo/README.md" \\
        soup python3 -m soup.funnel --readme /repo/README.md

Run after soup.novelty (it reads novelty_ranking.json). With --readme, the block between <!-- funnel:start --> and
<!-- funnel:end --> is rewritten. Levels:
  0 cheap surrogate evaluations (per run, every searcher's final count in runs/<run>/archive_s*.json, retired
    searchers included; repeats count again; distinct counted from the bitmaps where runs keep them)
  1 verified theories (results/*.json)            2 with a positive verified score (a proved emergent law)
  3 not a fragment of a named theory               4 candidates (top 20 non-fragments per run)
  5 distinct varieties (soup.dedupe)               6 not known to any check (N1 ranked)
  7 N1 with every automatic mark: an off-diagonal emergent law, no classical model, not related by hand
  8 studied closely (a memo notes/<key>.md, or a notes/*.md titled with the key) and not identified (no row in the ledger notes/rediscovery.md)
"""
import argparse
import glob
import json
import math
import os
import re
import time
from math import comb as _comb
from pathlib import Path

DIRS = ['.', 't4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x4a', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10', 'x11', 'x12-f5', 'x12-f6']
START, END = '<!-- funnel:start -->', '<!-- funnel:end -->'
EVAL_ONLY = {'x4a'}       # aborted after 3 min (deviation 6): its evaluations happened, its results are not used
MILESTONES = [(50e6, 'the dust removed'), (100e6, 'the surface scratched'), (200e6, 'digging')]


def _stats_evals(base):
    """Per run, the largest evals_total in logs/stats.jsonl (the supervisor's sum over its live searchers)."""
    per_run, p = {}, os.path.join(base, 'logs', 'stats.jsonl')
    if not os.path.exists(p): return per_run
    for line in open(p):
        try: r = json.loads(line)
        except ValueError: continue
        e = r.get('evals_total')
        for val in r.values():
            if e is None and isinstance(val, dict) and 'evals_total' in val: e = val['evals_total']
        if e is not None: per_run[r.get('run')] = max(per_run.get(r.get('run'), 0), e)
    return per_run


def _evals(base):
    """Cheap evaluations in one data directory (24 Nov 2026 correction). Per run, the sum of every searcher's final
    count in runs/<run>/archive_s*.json, which includes searchers the rebalancer retired; stats.jsonl drops those,
    and is used only for runs without archives (or where it is larger)."""
    st, tot = _stats_evals(base), 0
    runs = {os.path.basename(r) for r in glob.glob(os.path.join(base, 'runs', '*'))} | set(st)
    for run in runs:
        arch = sum(json.load(open(f)).get('evals', 0) for f in glob.glob(os.path.join(base, 'runs', str(run), 'archive_s*.json')))
        tot += max(arch, st.get(run, 0))
    return tot


def distinct(data='/data'):
    """Distinct law sets over every run with saved bitmaps (X7 on): linear counting on the union of all searchers'
    one-hash bitmaps (the hash is deterministic, so the union across runs is meaningful). Returns (distinct, raw of
    those runs), or None if no run has bitmaps."""
    import numpy as np
    union, raw = None, 0
    for d in DIRS:
        base = data if d == '.' else os.path.join(data, d)
        for rd in glob.glob(os.path.join(base, 'runs', '*')):
            bl = glob.glob(os.path.join(rd, 'bloom_*.npy'))
            if not bl: continue
            raw += sum(json.load(open(f)).get('evals', 0) for f in glob.glob(os.path.join(rd, 'archive_s*.json')))
            for f in bl:
                b = np.load(f); union = b.copy() if union is None else (union | b)
    if union is None: return None
    m = union.size * 8; fill = int(np.bitwise_count(union).sum(dtype=np.int64))
    return (int(round(-m * math.log(1 - fill / m))) if fill < m else None), raw


def compute(data='/data', notes='/notes'):
    lv = dict.fromkeys(range(9), 0)
    for d in DIRS:
        base = data if d == '.' else os.path.join(data, d)
        if not os.path.isdir(base): continue
        if d in EVAL_ONLY: lv[0] += _evals(base); continue
        rs =[json.load(open(f)) for f in glob.glob(os.path.join(base, 'results', '*.json'))]
        lv[0] += _evals(base); lv[1] += len(rs); lv[2] += sum(1 for r in rs if r.get('score', 0) > 0)
        fp = os.path.join(base, 'fragments.json')
        if os.path.exists(fp):
            lv[3] += sum(1 for r in json.load(open(fp))
                         if not r.get('fragment_of') and 'fragment' not in r.get('per_named', {}).values())
    cand = json.load(open(os.path.join(data, 'check', 'candidates.json')))
    dd = json.load(open(os.path.join(data, 'check', 'dedupe_candidates.json')))
    lv[4] = len(cand); lv[5] = len(cand) - sum(len(c) - 1 for c in dd['classes'])
    R = json.load(open(os.path.join(data, 'check', 'novelty_ranking.json')))['ranked']
    lv[6] = len(R)
    L7 = [r for r in R if r['offdiag_laws'] and not r['classical_models'] and not r['related']]
    lv[7] = len(L7)
    ledger = open(os.path.join(notes, 'rediscovery.md')).read()
    rows = '\n'.join(l for l in ledger.splitlines() if re.match(r'\| \d+ \|', l))
    # a memo: notes/<key>.md, or a notes/*.md whose title line (first line) names the key (memos on several candidates)
    titles = ' '.join(open(f).readline() for f in glob.glob(os.path.join(notes, '*.md')))
    memo = lambda k: os.path.exists(os.path.join(notes, k + '.md')) or k in titles
    L8 = [r for r in L7 if memo(r['key'][:8]) and r['key'][:8] not in rows]
    lv[8] = len(L8)
    return lv, [r['key'][:8] for r in L8]


ROWS = [
    (0, 'cheap evaluations', 'scored on 12,509 small structures; a theory seen twice counts twice'),
    (1, 'verified', 'through the provers and finite-model search'),
    (2, 'with a proved emergent law', 'synergy: implied by the theory, by no single law of it'),
    (3, 'not a fragment of a named theory', 'not part of lattices, quasigroups, skew lattices, ...'),
    (4, 'candidates', 'the top 20 non-fragments of each run'),
    (5, 'distinct varieties', 'equivalent candidates merged across runs (E both ways)'),
    (6, 'not known to any check', 'no split, definition, relabelling or catalogue match (N1)'),
    (7, 'every automatic mark', 'synergy off the diagonal, no classical model, nothing related found by hand'),
    (8, 'studied closely, still unidentified', 'a plain reading, models and a literature search, with Lean where a general statement emerged'),
]


def milestones(raw, dist):
    parts = [f'{v / 1e6:.0f}M, {name}: ' + ('**passed**' if raw >= v else f'{100 * raw / v:.0f}% of the way')
             for v, name in MILESTONES]
    d = ''
    if dist and dist[0]:
        d = (f' Distinct, where runs keep a bitmap (X7 on): {dist[0]:,} of their {dist[1]:,} raw evaluations '
             f'({100 * dist[0] / dist[1]:.1f}%).')
    return f'**Milestones** (raw level 0): {" · ".join(parts)}.{d}'


def block(lv, l8, dist=None):
    when = time.strftime('%d %b %Y, %H:%M UTC', time.gmtime())
    out = [START, f'*Regenerated by `soup.funnel` after each run\'s checks; last update {when}.*', '',
           '| level | theories | what survives |', '|---|---:|---|']
    for k, name, what in ROWS:
        n = f'{lv[k]:,}'
        if k >= 7: name, n = f'**{name}**', f'**{n}**'
        out.append(f'| {k} | {n} | {name}: {what} |')
    space = sum(_comb(71369, k) for k in range(1, 7))              # law sets of 1 to 6 laws (searcher.MAX_LAWS)
    out += ['', f'**The space:** {space:.2e} law sets of 1 to 6 laws. Level 0 is {lv[0] / space:.1e} of it '
            f'({100 * lv[0] / space:.1e} %), and an upper bound, since repeats count again.', '',
            milestones(lv[0], dist), '',
            f'Level 8: {", ".join(f"`{k}`" for k in l8) or "none"}. Not known is not new: no theory here is '
            'claimed new, and our literature searches are weak evidence.', END]
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--readme'); ap.add_argument('--notes', default='/notes')
    a = ap.parse_args()
    lv, l8 = compute(notes=a.notes)
    b = block(lv, l8, distinct()); print(b)
    if a.readme:
        p = Path(a.readme); t = p.read_text()
        i, j = t.index(START), t.index(END) + len(END)
        p.write_text(t[:i] + b + t[j:])


if __name__ == '__main__':
    main()
