"""N2: N1 with the gate's gaps closed (PREREGISTRATION.md, N2; post hoc, 28 Nov 2026). N1 (soup.novelty) is unchanged.

    python -m soup.novelty2 [--stage pre]

Same pool and the same six order keys as N1. Corrections:
  C1  check/hidden_param_candidates.json: definitional with a parameter is known;
  C2  ledger full identifications (LEDGER_N2), propagated to their dedupe class;
  C3  dedupe on the union corpus with three outcomes (check/dedupe2_candidates.json, soup.dedupe --union);
  C4  flags decided (check/decide_n2.json, soup.decide): decided known goes to the gate, decided not drops the flag,
      undecided stays and is marked;
  C5  a claim counts as proved only when Vampire or Twee confirms E's proof (check/reprove_n2.json, soup.reprove).
--stage pre applies C1-C3 only and writes check/n2_pre.json: the rows soup.decide and soup.reprove work on.
Writes check/novelty2_ranking.json and notes/candidates_table_n2.md (or check/ without /notes).
"""
import json
import os
import re
from pathlib import Path

import numpy as np

from .novelty import RELATED, LEDGER_KNOWN, _load, _match, _src_path, _verdict, _yn
from .paths import data

# full identifications in notes/rediscovery.md, fixed when N2 was preregistered (rows 6, 8, 9 are partial: RELATED)
LEDGER_N2 = dict(LEDGER_KNOWN, **{
    'a9295908': 'a fragment of Heyting algebras, with · = ∧ and x∘y = (y→x)→y (ledger row 11)',
    '71fd2cc6': 'commutative g-dimonoids plus x∘(x∘y) = x∘y (ledger row 13)',
})


def confirmed(proved, conf):
    """C5: the proved claims a second prover confirmed (conf: {claim index as str: bool})."""
    return [x for x in proved if conf.get(str(x['idx'])) is True]


def param_mark(hp):
    """C1: the 'known' text for a candidate soup.hidden --param marks definitional, else None."""
    if not hp or not hp.get('definitional'): return None
    return f"definitional with a parameter (soup.hidden --param): {(hp.get('matches') or ['?'])[0]}"


def build(stage='full'):
    from .core import ORDER
    from .data import NONDEG, PROBES, SIZES, sat_base, unpack_probes
    cands = _load('candidates.json')
    profs = {json.dumps(sorted(p['T'])): p for p in _load('profile_candidates.json', [])}
    split = {c['key']: c.get('split', 'not run') for c in _load('split_candidates.json', [])}
    hidden = {c['key']: c.get('definitional') for c in _load('hidden_candidates.json', [])}
    hparam = {c['key']: c for c in _load('hidden_param_candidates.json', [])}
    relab = {c['key']: c for c in _load('relabel_candidates.json', [])}
    r1 = (_load('rediscover.json', {}) or {}).get('sources', {})
    dd = _load('dedupe2_candidates.json')
    if dd is None: raise SystemExit('run soup.dedupe --union --out dedupe2 first (N2, C3)')
    rk = _load('ranking.json', {'candidates': []})
    t5a_rank = {r['key']: i for i, r in enumerate(rk['candidates'], 1)}
    t5a_equiv = {r['key']: r['equivalent_to'] for r in rk.get('excluded_equivalent', [])}
    classical = np.array([not re.match(r'(rand|all2)', name) for name, _ in PROBES])
    lit = _load('literature.json', {}) or {}
    decide = (_load('decide_n2.json', {}) or {}) if stage == 'full' else {}
    reprove = ((_load('reprove_n2.json', {}) or {}).get('confirmed', {})) if stage == 'full' else {}

    score = {c['key']: c.get('score') or 0 for c in cands}
    rep_of, related_of, ledger_of = {}, {}, {}
    for cls in dd['classes']:
        rep = max(cls, key=lambda k: score.get(k, 0))
        for k in cls:
            if k != rep: rep_of[k] = rep
        hit = next(((k, _match(RELATED, k)) for k in cls if _match(RELATED, k)), None)
        if hit:
            for k in cls: related_of[k] = hit[1] if k == hit[0] else f'{hit[1]} (same variety as {hit[0][:8]})'
        led = next(((k, _match(LEDGER_N2, k)) for k in cls if _match(LEDGER_N2, k)), None)
        if led:                                                   # C2: the identification belongs to the variety
            for k in cls: ledger_of[k] = led[1] if k == led[0] else f'{led[1]} (same variety as {led[0][:8]})'

    rows = []
    for c in cands:
        key, src = c['key'], c['source']
        row = {'key': key, 'source': src, 'laws': c['laws'], 'T': c['T'], 'score': c.get('score'),
               't5a_rank': t5a_rank.get(key), 'known': [], 'flags': [], 'undecided': [],
               'related': related_of.get(key) or _match(RELATED, key), 'literature': _verdict(lit.get(key))}
        rpath = _src_path(src, 'results', f'{key}.json')
        res = json.load(open(rpath)) if src != 'pilot' and os.path.exists(rpath) else None
        prof = profs.get(json.dumps(sorted(c['T'])), {})
        spec = prof.get('spectrum') or {}
        row['nondeg_sizes'] = sum(1 for s in spec.values() if (s.get('nondeg') or 0) > 0)
        row['axiom_size'] = int(sum(ORDER[t] for t in c['T']))
        row['record'] = res is not None
        proved = [x for x in (res or {}).get('claims', []) if x.get('status') == 'proved']
        conf = reprove.get(key, {})
        if stage == 'full':                                       # C5: only claims a second prover confirms
            ok = confirmed(proved, conf)
            row['unconfirmed'] = [x['law'] for x in proved if x not in ok]
            proved = ok
        row['proved_idx'] = [x['idx'] for x in proved]
        row['works'] = bool(res) and bool(proved) and row['nondeg_sizes'] >= 2
        # identification: N1's checks
        k = ledger_of.get(key) or _match(LEDGER_N2, key)
        if k: row['known'].append(f'ledger: {k}')                 # C2
        if t5a_equiv.get(key): row['known'].append(f'equivalent to a standard theory: {t5a_equiv[key]}')
        s = split.get(key, 'not run')
        dec = decide.get(key, {})
        if 'split' in dec: s = dec['split']                       # C4
        if s is True: row['known'].append('split: a ·-theory and a ∘-theory side by side (soup.split)')
        elif s is None or s == 'not run':
            (row['undecided'] if 'split' in dec else row['flags']).append(f'split {s}')
        if hidden.get(key): row['known'].append('definitional: one operation is a term in the other (soup.hidden)')
        pm = param_mark(hparam.get(key))                          # C1
        if pm: row['known'].append(pm)
        if res and res.get('screened'): row['known'].append(f"V4: {res['screened']}")
        rl = relab.get(key, {})
        for f, word in (('implies', 'implies'), ('fragment_of', 'fragment of'), ('equivalent_to', 'equivalent to')):
            for n in rl.get(f) or []:
                (row['flags'] if '?' in n else row['known']).append(f'soup.relabel: {word} {n}')
        decided_r1 = {(d['entry'], d['relabel'], d['kind']): d['outcome'] for d in dec.get('r1', [])}
        for x in r1.get(src, {}).get('relations', []):
            if x['key'] != key: continue
            text = f"R1: {x['kind']} of {x['entry']} ({x['relabel']})"
            if not x['kind'].endswith('?'): row['known'].append(text); continue
            out = decided_r1.get((x['entry'], x['relabel'], x['kind']))          # C4
            if out == 'known': row['known'].append(text.replace('?', '') + ' (decided, soup.decide)')
            elif out == 'not': pass
            elif out == 'undecided': row['undecided'].append(text)
            else: row['flags'].append(text)
        if key in rep_of: row['known'].append(f'same variety as {rep_of[key][:8]} (soup.dedupe, union corpus)')
        base = unpack_probes(sat_base(list(c['T'])))
        cl = np.flatnonzero(base & NONDEG & (SIZES >= 3) & classical)
        row['classical_models'] = len(cl)
        row['classical_example'] = PROBES[cl[0]][0] if len(cl) else None
        rows.append(row)

    gated = [r for r in rows if r['record'] and r['works'] and not r['known']]
    if stage == 'pre':
        return rows, gated
    from .core import Corpus
    from .offdiag import DIAG, offdiag_gain
    for src in sorted({r['source'] for r in gated}):              # one corpus per run, as N1's key
        C = Corpus(store=_src_path(src, 'corpus'))
        for r in (x for x in gated if x['source'] == src):
            g = offdiag_gain(C, sorted(r['T']))
            gs = set(g.tolist()) if g is not None else set()
            res = json.load(open(_src_path(r['source'], 'results', f"{r['key']}.json")))
            r['offdiag_laws'] = sorted({x['law'] for x in res.get('claims', [])
                                        if x['idx'] in r['proved_idx'] and not DIAG[x['idx']] and x['idx'] in gs})
    return rows, gated


def order(r):
    return (not r['offdiag_laws'], r['classical_models'] > 0, r['related'] is not None, -r['nondeg_sizes'],
            r['axiom_size'], -(r['score'] or 0))


def level7(rs): return [r for r in rs if r['offdiag_laws'] and not r['classical_models'] and not r['related']]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='full', choices=['pre', 'full'])
    a = ap.parse_args()
    rows, gated = build(a.stage)
    if a.stage == 'pre':
        out = [{'key': r['key'], 'source': r['source'], 'T': r['T'], 'laws': r['laws'], 'flags': r['flags'],
                'proved_idx': r['proved_idx']} for r in gated]
        json.dump(out, open(data('check', 'n2_pre.json'), 'w'), ensure_ascii=False, indent=1)
        print(f'N2 pre: {len(gated)} pass C1-C3; {sum(1 for r in gated if r["flags"])} carry a flag; '
              f'{sum(len(r["proved_idx"]) for r in gated)} proved claims to confirm')
        return
    ranked = sorted(gated, key=order)
    for i, r in enumerate(ranked, 1): r['n2_rank'] = i
    n1 = {r['key']: r for r in json.load(open(data('check', 'novelty_ranking.json')))['ranked']}
    for r in ranked: r['n1_rank'] = n1.get(r['key'], {}).get('n1_rank')
    dd = _load('dedupe2_candidates.json')
    L7 = level7(ranked)
    und = lambda rs: sum(1 for r in rs if r['undecided'] or r['flags'])
    levels = {'5': dd['level5'], '6': {'all': len(ranked), 'undecided': und(ranked)},
              '7': {'all': len(L7), 'undecided': und(L7)}}
    left = [k for k in n1 if k not in {r['key'] for r in ranked}]
    why = {}
    byk = {r['key']: r for r in rows}
    for k in left:
        r = byk[k]
        why[k] = r['known'][0] if r['known'] else ('fails works (no confirmed claim)' if r['record'] else 'no record')
    out = {'levels': levels, 'ranked': ranked, 'left_n1': why,
           'entered': [r['key'] for r in ranked if r['key'] not in n1],
           'known': [r for r in rows if r['known']],
           'not_works': [r for r in rows if r['record'] and not r['works'] and not r['known']]}
    json.dump(out, open(data('check', 'novelty2_ranking.json'), 'w'), ensure_ascii=False, indent=1)
    _table(out)
    print(json.dumps(levels))
    print(f'left N1\'s ranked list: {len(left)}; entered: {len(out["entered"])}')
    for k, w in why.items(): print(f'  {k[:8]} N1 {n1[k]["n1_rank"]:3d}: {w}')


def _table(out):
    lv = out['levels']
    L = ['# Candidates under N2 (post hoc; N1 is in candidates_table.md)', '',
         'Generated by `soup.novelty2` (PREREGISTRATION.md, N2). N2 is N1 with the gate\'s gaps closed: the parameter '
         'screen, ledger identifications, a union-corpus dedupe with three outcomes, decided flags, and a second prover '
         'for every claim. Nothing here is claimed to be new.', '',
         f"Level 5 between {lv['5']['lower']} and {lv['5']['upper']} varieties; level 6 {lv['6']['all']} "
         f"({lv['6']['undecided']} undecided); level 7 {lv['7']['all']} ({lv['7']['undecided']} undecided).", '',
         '| N2 | N1 | key | run | off-diagonal law | classical model | related to | sizes | axiom size | score | '
         'undecided | unconfirmed claims | laws |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in out['ranked']:
        L.append(f"| {r['n2_rank']} | {r['n1_rank'] or '-'} | `{r['key'][:8]}` | {r['source']} | "
                 f"{'; '.join(r['offdiag_laws'][:2]) or 'no'}{' …' if len(r['offdiag_laws']) > 2 else ''} | "
                 f"{_yn(r['classical_models'])} | {r['related'] or '-'} | {r['nondeg_sizes']} | {r['axiom_size']} | "
                 f"{r['score']} | {'; '.join(r['undecided'] + r['flags']) or '-'} | {len(r.get('unconfirmed', []))} | "
                 f"{' & '.join(r['laws'])} |")
    L += ['', f"## Left N1's ranked list ({len(out['left_n1'])})", '']
    L += [f"- `{k[:8]}`: {w}" for k, w in out['left_n1'].items()]
    target = Path('/notes') if Path('/notes').is_dir() else data('check')
    (target / 'candidates_table_n2.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
