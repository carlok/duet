"""R1 (PREREGISTRATION.md): which known structures of the catalogue did the search rediscover?

    python -m soup.rediscover --sources .,t4-prior,t4-noprior,x1,x2 [--jobs 6] [--secs 10] [--wall 7200]
    python -m soup.rediscover --summary [--candidates]

For each catalogue entry K (soup.catalogue.KNOWN), each of the 8 relabellings r (soup.relabel) and each verified
theory T of a source directory:
  fragment     every law of T follows from r(K), and T has a proved emergent law;
  subvariety   every law of r(K) follows from T;
  equivalent   both.
Model filter first: the corpus of the source directory plus the models of r(K) on 2-4 elements (Mace4, added in
memory only, never written to a store). Then E: secs per law, 500,000 processed clauses. Only proofs count; an E
timeout leaves the relation unknown. Post hoc; nothing here is read by the search or the score (rule 6).
Output: SOUP_DATA/check/rediscover.json.
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .paths import data, ensure

OUT = ('check', 'rediscover.json')


def theories(src):
    d = data('results') if src == '.' else data(src, 'results')
    out = []
    for f in sorted(d.glob('*.json')):
        try: r = json.load(open(f))
        except Exception: continue
        if not r.get('T'): continue
        out.append({'src': src, 'key': f.stem, 'T': sorted({int(t) for t in r['T']}), 'score': r.get('score', 0.0),
                    'emergent': any(c.get('status') == 'proved' for c in r.get('claims', []))})
    return out


def variants():
    """(entry, relabelling name, law tuple), deduplicated per entry."""
    from .catalogue import KNOWN, laws_of
    from .relabel import relabellings, relabel_law
    out = []
    for name in KNOWN:
        N0 = laws_of(name); seen = set()
        for rname, r in relabellings():
            N = tuple(sorted({relabel_law(i, r) for i in N0}))
            if None in N or N in seen: continue
            seen.add(N); out.append((name, rname, N))
    return out


def catalogue_models(V, sizes=(2, 3, 4), cap=200, secs=30):
    from .profile import all_models
    ms = []
    for _, _, N in V:
        for n in sizes:
            ms += [(n, F, G) for _, F, G in all_models(list(N), n, cap, secs)[0]]
    return ms


def _e(A, b, secs):
    from .provers import prove_e
    r = prove_e(sorted(A), b, processed_limit=500_000, cpu_limit=secs)
    return {'proved': True, 'countersatisfiable': False}.get(r['status'])


def run_source(src, V, models, cache, secs, jobs, deadline):
    from .core import Corpus
    C = Corpus(store=data('corpus') if src == '.' else data(src, 'corpus'))
    C.store = None                                  # catalogue models stay in memory
    for n, F, G in models: C.add('catalogue', n, F, G)
    TH = theories(src)
    want = {}                                       # (premises, goal) -> (premises list, goal)
    frag_cand, sub_cand = [], []
    for vi, (_, _, N) in enumerate(V):
        impN = C.implied(list(N))
        if impN is None: continue
        for ti, th in enumerate(TH):
            if all(impN[t] for t in th['T']):
                frag_cand.append((vi, ti))
                for t in th['T']:
                    if t not in N: want.setdefault((N, t), (list(N), t))
    for ti, th in enumerate(TH):
        impT = C.implied(th['T'])
        if impT is None: continue
        for vi, (_, _, N) in enumerate(V):
            if all(impT[v] for v in N):
                sub_cand.append((vi, ti))
                for v in N:
                    if v not in th['T']: want.setdefault((tuple(th['T']), v), (th['T'], v))
    todo = [k for k in want if repr(k) not in cache]
    skipped, i = 0, 0
    with ThreadPoolExecutor(jobs) as ex:                # E runs as a subprocess: threads are enough
        while i < len(todo):
            if time.time() > deadline: skipped = len(todo) - i; break
            chunk = todo[i:i + 4 * jobs]; i += len(chunk)
            futs = {ex.submit(_e, *want[k], secs): k for k in chunk}
            for f in as_completed(futs): cache[repr(futs[f])] = f.result()
    def holds(prem, goal):
        return True if goal in prem else cache.get(repr((tuple(prem), goal)))
    rel = []
    for vi, ti in frag_cand:
        name, rname, N = V[vi]; th = TH[ti]
        vals = [holds(N, t) for t in th['T']]
        if all(v is True for v in vals) and th['emergent']:
            rel.append({'entry': name, 'relabel': rname, 'key': th['key'], 'kind': 'fragment'})
        elif None in vals and False not in vals:
            rel.append({'entry': name, 'relabel': rname, 'key': th['key'], 'kind': 'fragment?'})
    for vi, ti in sub_cand:
        name, rname, N = V[vi]; th = TH[ti]
        vals = [holds(th['T'], v) for v in N]
        if all(v is True for v in vals):
            rel.append({'entry': name, 'relabel': rname, 'key': th['key'], 'kind': 'subvariety'})
        elif None in vals and False not in vals:
            rel.append({'entry': name, 'relabel': rname, 'key': th['key'], 'kind': 'subvariety?'})
    both = {(r['entry'], r['relabel'], r['key']) for r in rel if r['kind'] == 'fragment'} & \
           {(r['entry'], r['relabel'], r['key']) for r in rel if r['kind'] == 'subvariety'}
    rel += [{'entry': e, 'relabel': rn, 'key': k, 'kind': 'equivalent'} for e, rn, k in sorted(both)]
    return {'theories': len(TH), 'e_jobs': len(todo), 'e_skipped_wall': skipped, 'relations': rel,
            'unknown': sum(1 for k in todo if cache.get(repr(k)) is None)}


def summary(res, with_candidates=False):
    from .catalogue import KNOWN
    srcs = list(res['sources'])
    found = {}
    print('| entry | post hoc | ' + ' | '.join(f'{s} frag / sub / eq' for s in srcs) + ' |')
    print('| --- | --- | ' + ' | '.join('---' for _ in srcs) + ' |')
    for name, k in KNOWN.items():
        cells = []
        for s in srcs:
            rel = res['sources'][s]['relations']
            c = {kind: len({r['key'] for r in rel if r['entry'] == name and r['kind'] == kind})
                 for kind in ('fragment', 'subvariety', 'equivalent')}
            if c['fragment'] or c['equivalent']: found.setdefault(name, []).append(s)
            cells.append(f"{c['fragment']} / {c['subvariety']} / {c['equivalent']}")
        print(f"| {name} | {'yes' if k['post_hoc'] else ''} | " + ' | '.join(cells) + ' |')
    n_all = len(found); n_pre = len([n for n in found if not KNOWN[n]['post_hoc']])
    print(f"\nRediscovered (fragment or equivalent, at least once): {n_all} of {len(KNOWN)}; "
          f"without post hoc entries {n_pre} of {sum(not k['post_hoc'] for k in KNOWN.values())}")
    print('Not rediscovered:', ', '.join(n for n in KNOWN if n not in found) or 'none')
    for s in srcs:
        r = res['sources'][s]
        print(f"{s}: {r['theories']} theories, {r['e_jobs']} E jobs, {r['unknown']} unknown, "
              f"{r['e_skipped_wall']} skipped at the wall cap")
    if with_candidates:
        cand = json.load(open(data('check', 'candidates.json')))
        split = {c['key']: c.get('split') for c in json.load(open(data('check', 'split_candidates.json')))}
        relab = {c['key']: c for c in json.load(open(data('check', 'relabel_candidates.json')))}
        cat = {}
        for s in srcs:
            for r in res['sources'][s]['relations']:
                if r['kind'] in ('fragment', 'subvariety', 'equivalent'): cat.setdefault(r['key'], set()).add(r['entry'])
        print('\nTop non-fragment candidates identified, by source (split / division / catalogue / any):')
        for s in sorted({c['source'] for c in cand}):
            cs = [c for c in cand if c['source'] == s]
            sp = [c for c in cs if split.get(c['key']) is True]
            dv = [c for c in cs if any('quasigroup' in t for t in relab.get(c['key'], {}).get('implies', []))]
            ct = [c for c in cs if c['key'] in cat]
            anyk = {c['key'] for c in sp + dv + ct}
            print(f"  {s}: {len(cs)} candidates; split {len(sp)}, division {len(dv)}, catalogue {len(ct)}, "
                  f"identified {len(anyk)} ({100 * len(anyk) / max(1, len(cs)):.0f}%)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sources', default='.,t4-prior,t4-noprior,x1,x2')
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--secs', type=int, default=10)
    ap.add_argument('--wall', type=int, default=7200)
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--candidates', action='store_true')
    a = ap.parse_args()
    out = data(*OUT)
    if a.summary:
        summary(json.load(open(out)), a.candidates); return
    res = json.load(open(out)) if out.exists() else {'sources': {}, 'cache': {}}
    deadline = time.time() + a.wall
    V = variants()
    print(f'{len(V)} catalogue variants; Mace4 models of each on 2-4 elements ...', flush=True)
    models = catalogue_models(V)
    print(f'{len(models)} catalogue models', flush=True)
    for src in a.sources.split(','):
        t0 = time.time()
        r = run_source(src, V, models, res['cache'], a.secs, a.jobs, deadline)
        r['secs'] = round(time.time() - t0, 1); res['sources'][src] = r
        ensure('check'); json.dump(res, open(out, 'w'), ensure_ascii=False)
        print(f"{src}: {r['theories']} theories, {len(r['relations'])} relations, {r['e_jobs']} E jobs, "
              f"{r['unknown']} unknown, {r['secs']} s", flush=True)
    summary(res)


if __name__ == '__main__':
    main()
