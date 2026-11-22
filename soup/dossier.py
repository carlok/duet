"""Candidates, the preregistered T5a ranking, and dossiers (PREREGISTRATION.md, T5a "Use in ranking").

    python -m soup.dossier candidates [--sources t4-prior,t4-noprior,.,x1] [--top 20]
        non-fragment theories, the top N by score from each source's fragments.json (source '.' = SOUP_DATA itself,
        the earlier runs), plus T1 and T2 -> SOUP_DATA/check/candidates.json
    python -m soup.profile --set candidates --jobs 8        (profiles -> check/profile_candidates.json)
    python -m soup.dossier rank      -> check/ranking.json and a table (uses check/t5a_report.json)
    python -m soup.dossier write [--top 5]                  -> SOUP_DATA/dossiers/<name>.md

Ranking, fixed before any T4 theory was profiled:
  1. exclude fragments of a named theory (fragments.py 'fragment_of') and theories that soup.equiv finds
     equivalent to a standard theory;
  2. rank by the number of calibrated features (t5a_report 'calibrated') the theory has; ties by duality, then by
     the number of sizes with non-degenerate models, then by score;
  3. if no feature is calibrated, nothing is ranked: candidates are listed with their features.
Scores of the earlier runs are V1 scores, of T4 V2, of X1 V3; they only break ties within the rubric.
"""
import argparse
import json

from .paths import data, ensure

T1 = ['(x·x)∘x = x', '((x·(y·z))∘z)·y = y']
T2 = ['x∘(y·(y∘x)) = x', 'x·((x∘x)·y) = x']


def candidates(sources, top):
    from .named import law_index
    out = []
    for src in sources:
        path = data('fragments.json') if src == '.' else data(src, 'fragments.json')
        if not path.exists(): print('no fragments.json for', src); continue
        rows = [r for r in json.load(open(path)) if not r['fragment_of']]
        rows.sort(key=lambda r: -(r.get('score') or 0))
        for r in rows[:top]:
            out.append({'source': src, 'key': r['key'], 'T': r['T'], 'laws': r['laws'], 'score': r.get('score'),
                        'dualities': r.get('dualities', []), 'undecided': r.get('undecided', [])})
    for name, laws in (('T1', T1), ('T2', T2)):
        T = sorted(law_index(s.replace(' ', '')) for s in laws)
        out.append({'source': 'pilot', 'key': name, 'T': T, 'laws': laws, 'score': None, 'dualities': [], 'undecided': []})
    seen, uniq = set(), []
    for c in out:                                       # the same theory from two sources: keep the first
        k = json.dumps(sorted(c['T']))
        if k not in seen: seen.add(k); uniq.append(c)
    json.dump(uniq, open(ensure('check') / 'candidates.json', 'w'), ensure_ascii=False, indent=1)
    print(len(uniq), 'candidates written to check/candidates.json')


def rank():
    from .core import Corpus
    from .equiv import equivalent
    cands = json.load(open(data('check', 'candidates.json')))
    profs = {json.dumps(sorted(p['T'])): p for p in json.load(open(data('check', 'profile_candidates.json')))}
    t5a = json.load(open(data('check', 't5a_report.json')))
    cal = t5a['calibrated']
    rerun = data('check', 't5a_report_t3_rerun.json')          # deviation 3: features calibrated in both analyses
    if rerun.exists(): cal = [f for f in cal if f in json.load(open(rerun))['calibrated']]
    C = Corpus(store=data('corpus'))
    rows = []
    for c in cands:
        p = profs.get(json.dumps(sorted(c['T'])), {})
        feats = p.get('features') or {}
        eq = equivalent(c['T'], C)
        nd_sizes = sum(1 for s in (p.get('spectrum') or {}).values() if s.get('nondeg'))
        rows.append(dict(c, equivalent_to=eq, features=feats, profile_status=p.get('status', 'ok' if p else 'missing'),
                         n_calibrated=sum(bool(feats.get(f)) for f in cal), nondeg_sizes=nd_sizes))
    kept = [r for r in rows if not r['equivalent_to']]
    if cal:
        kept.sort(key=lambda r: (-r['n_calibrated'], -bool(r['dualities'] or (r['features'] or {}).get('duality')),
                                 -r['nondeg_sizes'], -(r['score'] or 0)))
    out = {'calibrated_features': cal, 'ranked': bool(cal), 'excluded_equivalent': [r for r in rows if r['equivalent_to']],
           'candidates': kept}
    json.dump(out, open(ensure('check') / 'ranking.json', 'w'), ensure_ascii=False, indent=1)
    print('calibrated features:', cal or 'none (listed, not ranked)')
    print(len(out['excluded_equivalent']), 'excluded as equivalent to a standard theory')
    for i, r in enumerate(kept[:30], 1):
        f = ' '.join(k for k, v in (r['features'] or {}).items() if v) or '-'
        print(f"{i:2d} {r['source']:10s} {str(r['key'])[:8]:8s} calib {r['n_calibrated']} | {f} | nondeg sizes "
              f"{r['nondeg_sizes']} | score {r['score']} | {' & '.join(r['laws'])[:120]}")


def write(top):
    rk = json.load(open(data('check', 'ranking.json')))
    profs = {json.dumps(sorted(p['T'])): p for p in json.load(open(data('check', 'profile_candidates.json')))}
    d = ensure('dossiers')
    for i, r in enumerate(rk['candidates'][:top], 1):
        p = profs.get(json.dumps(sorted(r['T'])), {})
        name = f"{i:02d}-{str(r['key'])[:8]}"
        L = [f"# Candidate {i}: `{str(r['key'])[:8]}` ({r['source']})", '',
             'Status: **candidate**, not a result (rule 4). The literature check and the equivalence checks are below.',
             '', '## Laws', '', *[f'- `{s}`' for s in r['laws']], '',
             f"Duality: {', '.join(r['dualities']) or (p.get('duality') and ', '.join(p['duality'])) or 'none'}. "
             f"Score: {r['score']}. Not a fragment of the 10 named theories (undecided for: "
             f"{', '.join(r['undecided']) or 'none'}). Equivalent to a standard theory: no.", '',
             '## Profile (`soup.profile`)', '']
        if p:
            L += [f"- Features: {', '.join(k for k, v in p['features'].items() if v) or 'none'}"
                  f" (calibrated by T5a: {', '.join(rk['calibrated_features']) or 'none'})",
                  f"- Spectrum (non-degenerate models up to isomorphism): "
                  + ', '.join(f"{n}: {s['nondeg']}{'' if s['complete'] else '+'}" for n, s in p['spectrum'].items()),
                  f"- Free algebra on 1 / 2 generators (on the models): {p.get('clone1', {}).get('functions')}"
                  f"{'' if p.get('clone1', {}).get('closed') else ' (not closed)'} / {p.get('clone2', {}).get('functions')}"
                  f"{'' if p.get('clone2', {}).get('closed') else ' (not closed)'}",
                  '- Mal\'cev-type terms (proved by E): ' + (', '.join(f"{k}: `{v['term']}`" for k, v in
                                                                   (p.get('malcev') or {}).items() if v.get('proved')) or 'none'),
                  f"- Convergent presentation: {p['convergent']}",
                  f"- ETP numbers with x·y = x∘y: {p.get('etp')}"]
            sm = p.get('smallest_nondeg')
            if sm:
                L += ['', f"Smallest non-degenerate model ({sm['n']} elements), rows x, columns y:", '', '```',
                      '·  ' + '  '.join(' '.join(map(str, row)) for row in sm['F']), '∘  ' + '  '.join(' '.join(map(str, row)) for row in sm['G']), '```']
        L += ['', '## Literature check', '', 'To do: search for the laws and for the structure of the models.', '',
              '## Lean', '', 'To do: certificates for the finite facts (`soup.lean_cert`).', '']
        (d / f'{name}.md').write_text('\n'.join(L))
        print('wrote', d / f'{name}.md')


NONDEG = ['x · y = x', 'x · y = y', 'x ∘ y = x', 'x ∘ y = y', 'x · y = x ∘ y', 'x · y = y ∘ x']


def lean_json(top):
    """For the top candidates: the smallest non-degenerate model with the non-degeneracy laws it refutes (projections,
    equal or opposite operations), checked by check_offline.check_finite (two evaluators), as a model JSON for
    soup.lean_cert -> check/cand<i>_model.json."""
    from .check_offline import check_finite
    from .data import LAWS
    from .named import law_index
    rk = json.load(open(data('check', 'ranking.json')))
    profs = {json.dumps(sorted(p['T'])): p for p in json.load(open(data('check', 'profile_candidates.json')))}
    for i, r in enumerate(rk['candidates'][:top], 1):
        sm = profs[json.dumps(sorted(r['T']))].get('smallest_nondeg')
        if not sm: print(i, r['key'], 'no small model'); continue
        cl = [law_index(s.replace(' ', '')) for s in NONDEG]
        chk = check_finite(r['T'], cl, sm['F'], sm['G'])
        refuted = {s: {'refuted': True} for s, c in zip(NONDEG, cl) if chk['claims_fail'][LAWS[c]]}
        assert all(chk['axioms_hold'].values()) and chk['law_vector_agrees'] and chk['nondeg'], chk
        out = {'key': r['key'], 'laws': r['laws'], 'n': sm['n'], 'F': sm['F'], 'G': sm['G'], 'claims': refuted,
               'source': f"work/check/profile_candidates.json (smallest non-degenerate model, candidate {i})"}
        json.dump(out, open(ensure('check') / f'cand{i}_model.json', 'w'), ensure_ascii=False, indent=1)
        print(i, r['key'], f"n = {sm['n']}", 'refutes', list(refuted))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['candidates', 'rank', 'write', 'lean-json'])
    ap.add_argument('--sources', default='t4-prior,t4-noprior,.'); ap.add_argument('--top', type=int, default=20)
    a = ap.parse_args()
    if a.cmd == 'candidates': candidates(a.sources.split(','), a.top)
    elif a.cmd == 'rank': rank()
    elif a.cmd == 'lean-json': lean_json(a.top if a.top != 20 else 5)
    else: write(a.top if a.top != 20 else 5)


if __name__ == '__main__':
    main()
