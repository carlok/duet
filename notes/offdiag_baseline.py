"""Off-diagonal synergy in a run that did not select for it (PREREGISTRATION.md, X4, post hoc baseline).

    podman run -i --rm -v "$PWD/work:/data:ro" -e SOUP_DATA=/data/x3 soup python3 - [x3] < notes/offdiag_baseline.py

For every theory of the run with a positive verified score, on the run's final corpus:
- whether its off-diagonal gain (soup.offdiag, with the widened diagonal of deviation 6) is non-empty;
- whether one of its proved emergent laws is off-diagonal: not a diagonal law, and in that gain.
X4 selected for the second by construction (V5), so this measures how often it happens without selection.
"""
import glob
import json
import sys

from soup.core import Corpus
from soup.offdiag import DIAG, offdiag_gain
from soup.paths import data

run = sys.argv[1] if len(sys.argv) > 1 else 'x3'
C = Corpus(store=data('corpus'))
R = [json.load(open(f)) for f in glob.glob(str(data('results')) + '/*.json')]
pos = [r for r in R if r.get('score', 0) > 0]
nonempty = proved_off = 0
for r in pos:
    g = offdiag_gain(C, sorted(r['T']))
    gs = set(g.tolist()) if g is not None else set()
    nonempty += bool(gs)
    if any(c['status'] == 'proved' and not DIAG[c['idx']] and c['idx'] in gs for c in r.get('claims', [])):
        proved_off += 1
print(f'{run}: corpus {len(C)} found structures; {len(pos)} theories with positive score')
print(f'  non-empty off-diagonal gain on the corpus: {nonempty} ({100 * nonempty / len(pos):.1f}%)')
print(f'  a proved emergent law that is off-diagonal: {proved_off} ({100 * proved_off / len(pos):.1f}%)')
