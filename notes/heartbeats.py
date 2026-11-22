"""Searcher heartbeats at the end of a run: evaluations, pushes, and theories skipped as lattice-valid (arm fusion).

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - <dir> < notes/heartbeats.py
"""
import glob
import json
import sys

d = sys.argv[1] if len(sys.argv) > 1 else 'x4'
hs = [json.load(open(f)) for f in sorted(glob.glob(f'/data/{d}/logs/workers/s*.json'))]
for h in hs:
    print(f"{h.get('name')}: evals {h.get('evals')}, pushed {h.get('pushed')}, lattice-skipped {h.get('lat_skipped')}, ignore-skipped {h.get('ign_skipped')}")
e, s = sum(h.get('evals') or 0 for h in hs), sum(h.get('lat_skipped') or 0 for h in hs)
print(f'{d}: {s} of {e} evaluations skipped as lattice-valid ({100 * s / max(e, 1):.1f}%)')
