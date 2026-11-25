"""X9 predictions S1-S4 (PREREGISTRATION.md, X9), from x9's results, its stats log and X8's copied queue.

    podman run -i --rm -v "$PWD/work:/data:ro" soup python3 - < notes/x9_predictions.py
"""
import collections
import glob
import json
import os

D, X8 = '/data/x9', '/data/x8'
key = lambda f: os.path.basename(f)[:-5].split('_', 1)[1]
rs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{D}/results/*.json')}
copied_b = {key(f) for f in glob.glob(f'{X8}/queue/stage2c/*.json')}      # their stage-b results were copied too
copied_p = {key(f) for f in glob.glob(f'{X8}/queue/pending/*.json')}
mine = {k: r for k, r in rs.items() if r.get('run') == 'x9'}
ab = {k: r for k, r in mine.items() if r.get('stage') in ('a', 'b')}
print(f'results {len(rs)}: run x9 {len(mine)} (stage a {sum(r["stage"] == "a" for r in mine.values())}, '
      f'b {sum(r["stage"] == "b" for r in mine.values())}, c {sum(r["stage"] == "c" for r in mine.values())}); '
      f'copied stage-b results still as copied {sum(1 for k in rs if k in copied_b and rs[k].get("run") != "x9")}')

# verifier-hours: time integral of the live verifier count in logs/stats.jsonl (each line holds until the next)
L = [json.loads(l) for l in open(f'{D}/logs/stats.jsonl')]
vh = sum(L[i]['n_verify'] * (L[i + 1]['t'] - L[i]['t']) for i in range(len(L) - 1)) / 3600
wall = (L[-1]['t'] - L[0]['t']) / 3600
print(f'wall {wall:.2f} h, verifier-hours {vh:.2f}, searchers ever {max(s["n_search"] for s in L)}, '
      f'evals {L[-1]["evals_total"]}')
s1 = len(ab) / vh
print(f'S1: {len(ab)} theories through stages a and b in {vh:.2f} verifier-hours = {s1:.1f} per verifier-hour '
      f'-> {"holds" if s1 >= 25 else "fails"} (>= 25; x8b 16.9)')

c = {k: r for k, r in mine.items() if r.get('stage') == 'c'}
secs = {k: (r.get('secs') or {}).get('c', 0.0) for k, r in c.items()}
mean = sum(secs.values()) / max(1, len(secs)) / 60
busy = [s for s in secs.values() if s > 0]
print(f'S2: {len(c)} theories through stage c, all copied: {all(k in copied_b for k in c)}; minutes '
      f'{sorted(round(s / 60, 1) for s in secs.values())}')
print(f'  mean {mean:.1f} min -> {"holds" if mean <= 35 else "fails"} (<= 35; x8b 70.6)')
print(f'  {len(c) - len(busy)} had no claim left open: X8\'s post-run linear sweep (--write) had refuted them in the '
      f'copied results; mean of the other {len(busy)}: {sum(busy) / max(1, len(busy)) / 60:.1f} min')
lin_c = collections.Counter(cl['linear']['status'] for r in c.values() for cl in r['claims']
                            if (cl.get('linear') or {}).get('qmax') == 64)
print(f'  stage-c linear screen (q <= 64): {dict(lin_c)}')
start = collections.Counter(s['queue']['stage2c'] for s in L[:1]); end = L[-1]['queue']['stage2c']
print(f'  stage-c lane: {L[0]["queue"]["stage2c"]} at the start, {end} at the end')

lin = [cl for r in ab.values() for cl in r.get('claims', []) if (cl.get('linear') or {}).get('qmax') == 32]
st = collections.Counter(cl['linear']['status'] for cl in lin)
ref = st.get('refuted', 0)
sizes = collections.Counter(cl['linear']['q'] for cl in lin if cl['linear']['status'] == 'refuted')
fam = collections.Counter(cl['linear']['family'] for cl in lin if cl['linear']['status'] == 'refuted')
tl = sum(cl['linear']['secs'] for cl in lin)
print(f'S3: linear screen ran on {len(lin)} stage-b claims: {dict(st)}; refuted {ref} = {100 * ref / max(1, len(lin)):.1f}% '
      f'-> {"holds" if ref >= 0.05 * len(lin) else "fails"} (>= 5%)')
print(f'  sizes {dict(sorted(sizes.items()))}; families {dict(fam)}; {tl / 3600:.2f} h in all, '
      f'mean {tl / max(1, len(lin)):.1f} s per claim')

got = copied_p & set(mine)
print(f'S4: {len(got)} of the {len(copied_p)} copied pending theories have a result in x9 '
      f'-> {"holds" if len(got) >= 1000 else "fails"} (>= 1,000); new from searchers: '
      f'{len(set(mine) - copied_p - copied_b)}')
left = {key(f) for f in glob.glob(f'{D}/queue/pending/*.json')} | {key(f) for f in glob.glob(f'{D}/queue/stage2c/*.json')}
print(f'  of the copied pending without a result: {len(copied_p - set(mine))}, '
      f'still queued {len((copied_p - set(mine)) & left)}')

claims = [cl for r in mine.values() for cl in r.get('claims', [])]
out = collections.Counter()
for cl in claims:
    s = cl['status']
    out['proved' if s == 'proved' else 'E saturation' if 'saturation' in s else 'linear' if 'model over' in s
        else 'FMB' if 'FMB' in s else 'finite model' if s.startswith('false') else s] += 1
print(f'claims {len(claims)}: {dict(out)}; z3 skipped after E {sum(1 for cl in claims if cl.get("z3_skipped"))}')
pos = sum(1 for r in mine.values() if (r.get('score') or 0) > 0)
scr = collections.Counter(r.get('screened') for r in mine.values() if r.get('screened'))
print(f'positive score {pos}; screened {dict(scr)}; top {max((r.get("score") or 0) for r in mine.values()):.3f}')
tb = sum(r.get('secs_b') or 0 for r in ab.values()) / 3600; ta = sum(r.get('secs_a') or 0 for r in ab.values()) / 3600
print(f'stage a {ta:.2f} h, stage b {tb:.2f} h over {len(ab)} theories ({3600 * tb / max(1, len(ab)):.0f} s mean in b)')
print(f'copied x8b results (stages a and b under V6), reported apart: {len(copied_b)}; of them through stage c in x9: '
      f'{len(set(c) & copied_b)}')
