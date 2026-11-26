"""How the search-side parameter-disguise skip (soup.paramskip, arm fusion5) agrees with V6's screen (26 Nov 2026).

    podman run -i --rm -v "$PWD/work:/data:ro" -e SOUP_DATA=/data/x10 soup python3 - [confirm max_n] < notes/paramskip_check.py

Corpus: x10's (the one a next run would start from), kept in memory: Mace4's countermodels are added to it as a run
would add them, but not written. For every result of X5 to X10: does the skip fire, and did V6's screen mark it a
parameter definition (X5 ran V5, without the screen)? Then the candidates (check/candidates.json), where a skip would
be a loss, with their N1 status. Argument 'corpus' runs step 1 alone; 'confirm 4' (the default) adds the Mace4 step on
2 to 4 elements.
"""
import collections
import glob
import json
import sys
import time

from soup.core import Corpus
from soup.paramskip import NTERMS, ParamSkip, term_str
from soup.paths import data

mode = sys.argv[1] if len(sys.argv) > 1 else 'confirm'
max_n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
t0 = time.time()
C = Corpus(store=data('corpus')); C.store = None             # read the store, write nothing
PS = ParamSkip(C, confirm=(mode == 'confirm'), max_n=max_n)
print(f'mode {mode}, max_n {max_n}; corpus {len(C)} found structures, {PS.nb} base; {NTERMS} terms; '
      f'ready in {time.time() - t0:.0f} s', flush=True)
PS.matches([0, 1])                                     # compile

LEVEL8 = ['bc43fd42', 'de0c0cf3', 'd0e963d9', 'd14ced44', '3818b88f', '55cb2c91', '1d0a5211', '742cc445', '97a7dfcf']


def v6_kind(r):
    """What V6's screen said about a theory the skip fires on: its census models (Mace4, sizes 2-4) matched no term
    ('census refutes'); E saturated on every matched term ('E refutes'); or a matched term stayed unproved."""
    p = (r.get('screen') or {}).get('param')
    if p is None: return 'screen not run'
    st = [x.get('e') for x in p.get('matches', [])]
    if not st: return 'census refutes'
    if all(s == 'countersatisfiable' for s in st): return 'E refutes'
    return 'census agrees, E open'


def first(T):
    m = PS.matches(T)
    return term_str(m[0]) if len(m) else '-'


secs, fp = [], []
for d in ('x5', 'x6', 'x7', 'x8', 'x9', 'x10'):
    tab = collections.Counter()
    for f in sorted(glob.glob(f'/data/{d}/results/*.json')):
        r = json.load(open(f))
        t = time.time(); s = PS.check(r['T']); secs.append(time.time() - t)
        v6 = r.get('screened') == 'parameter definition'
        tab[(s, v6)] += 1
        if s and not v6 and d != 'x5': fp.append((d, r['key'][:8], r.get('score'), first(r['T']), v6_kind(r)))
    n = sum(tab.values())
    print(f'{d}: {n} results; skip and V6 {tab[(True, True)]}, skip only {tab[(True, False)]}, '
          f'V6 only {tab[(False, True)]}, neither {tab[(False, False)]}', flush=True)
print(f'check time: mean {1000 * sum(secs) / len(secs):.1f} ms, max {1000 * max(secs):.0f} ms over {len(secs)}; '
      f'step 1 fired {PS.fired}, Mace4 calls {PS.mace_calls} ({PS.mace_secs:.0f} s, '
      f'{PS.mace_secs / max(1, PS.mace_calls):.2f} s each), countermodels added {PS.added}')

print(f'\nskipped, not marked by V6 ({len(fp)}), X6-X10, by what V6 said (positive verified score in brackets):')
k = collections.Counter(x[4] for x in fp); kp = collections.Counter(x[4] for x in fp if (x[2] or 0) > 0)
for name, v in k.most_common(): print(f'  {name}: {v} ({kp[name]})')
print('  examples with a positive score:')
for x in [x for x in fp if (x[2] or 0) > 0][:15]: print('   ', *x)

print('\ncandidates (check/candidates.json), with their N1 status (check/novelty_ranking.json):')
N = json.load(open('/data/check/novelty_ranking.json'))
status = {}
for c in N['ranked']: status[c['key']] = f"N1 rank {c['n1_rank']}, classical {c['classical_models']}"
for c in N['known']: status[c['key']] = f"known: {c['literature'][:60]}"
for c in N['not_works']: status[c['key']] = 'fails works'
lvl7 = {c['key'] for c in N['ranked'] if c.get('offdiag_laws') and c['classical_models'] == 0 and not c.get('related')}
cands = json.load(open('/data/check/candidates.json'))
hit = [(c['source'], str(c['key']), first(c['T'])) for c in cands if PS.check(c['T'])]
kind = lambda key: status.get(key, '-').split(',')[0].split(':')[0].split(' rank')[0]
print(f'  {len(hit)} of {len(cands)} would be skipped; by N1 status: {dict(collections.Counter(kind(h[1]) for h in hit))}; '
      f'level 7 (of {len(lvl7)}): {sum(h[1] in lvl7 for h in hit)}; level 8: {sum(h[1][:8] in LEVEL8 for h in hit)}')
for s, key, t in hit:
    print(f'   {s:10s} {key[:8]} {t:40s} {status.get(key, "-")}{"  LEVEL 7" if key in lvl7 else ""}')
