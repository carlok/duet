"""X11's REPORT table: its results (one block, x11a), beside X10's own (both blocks, the copied X9 tasks left out).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x11_table.py

Claim outcomes as in notes/x10_table.py.
"""
import collections
import glob
import json
import os

qkey = lambda f: os.path.basename(f)[:-5].split('_', 1)[1]
copied = {qkey(f) for f in glob.glob('/data/x9/queue/stage2c/*.json')}


def results(d):
    return {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'/data/{d}/results/*.json')}


def outcome(c):
    s = c['status']
    if s == 'proved': return 'proved'
    if 'Vampire FMB' in s: return 'FMB'
    if 'linear model' in s: return 'linear'
    if 'E saturation' in s: return 'E saturation'
    if s.startswith('false'): return 'finite (stage a/c)'
    return s


def row(R):
    claims = [c for r in R for c in r.get('claims', [])]
    st = collections.Counter(outcome(c) for c in claims)
    sec = lambda st_: sum((r.get('secs') or {}).get(st_, 0) for r in R) / 3600
    nb = sum(1 for r in R if (r.get('secs') or {}).get('b'))
    scr = collections.Counter(r.get('screened') for r in R if r.get('screened'))
    return {
        'theories': len(R),
        'through stage c': sum(r.get('stage') == 'c' for r in R),
        'positive score': sum((r.get('score') or 0) > 0 for r in R),
        'screened param / split': f"{scr.get('parameter definition', 0)} / {scr.get('split', 0)}",
        'stage a / b / c hours': f"{sec('a'):.2f} / {sec('b'):.2f} / {sec('c'):.2f}",
        'mean stage b per theory (s)': f"{3600 * sec('b') / max(1, nb):.0f}",
        'claims / proved': f"{len(claims)} / {st['proved']}",
        'refuted: finite (a/c) / FMB / linear / E sat': (f"{st['finite (stage a/c)']} / {st['FMB']} / {st['linear']} / "
                                                         f"{st['E saturation']}"),
        'unknown / open': f"{st['unknown']} / {st['open']}",
        'other outcomes': {k: v for k, v in st.items() if k not in ('proved', 'FMB', 'linear', 'E saturation',
                                                                     'finite (stage a/c)', 'unknown', 'open')},
    }


x11, x10 = results('x11'), results('x10')
groups = collections.OrderedDict()
groups['X11 (x11a)'] = [r for r in x11.values() if str(r.get('run', '')).startswith('x11')]
groups['X10 own'] = [r for k, r in x10.items() if str(r.get('run', '')).startswith('x10') and k not in copied]
rows = {g: row(R) for g, R in groups.items()}
for name in rows['X11 (x11a)']:
    print(f'{name:45s} ' + ' | '.join(f'{g}: {rows[g][name]}' for g in rows))
