"""N1: a novelty ranking of the candidate pool, next to the T5a ranking (PREREGISTRATION.md, N1; post hoc).

    python -m soup.novelty [--readme /repo/README.md]

With --readme, the block between <!-- candidates:start --> and <!-- candidates:end --> in the README is rewritten:
the metric, the counts, and the N1 top 10 (a live summary, regenerated after every run's checks).

Reads work/check/{candidates,profile_candidates,split_candidates,hidden_candidates,relabel_candidates,rediscover,
dedupe_candidates,ranking}.json and each run's results/ and corpus/. Writes work/check/novelty_ranking.json and
notes/candidates_table.md (known / not known as far as our checks and searches go).

Gate: works (a proved emergent law, non-degenerate models on >= 2 sizes); nothing identifies it (split, definitional,
V4 mark, soup.relabel relation, R1 relation; split None and R1 '?' are allowed and flagged); one per dedupe class.
Order: off-diagonal proved emergent law; no classical model; not related (ledger, partial identification); more
non-degenerate sizes; smaller axioms; verified score.
"""
import json
import os
import re
from pathlib import Path

import numpy as np

from .paths import data

# partial identifications from the ledger (notes/rediscovery.md), fixed when N1 was preregistered
RELATED = {
    '10c98c4b': 'core = Δ-bijective pair (Dehornoy 2015; Bonatto et al.); full theory: no source found',
    '3e068fa6': 'half of the Δ-bijective core; its finite models are Δ-bijective pairs',
    '31d6d970': 'associative case = rectangular skew lattices (Leech 2020); full theory: no source found',
}
# full identifications from the ledger that no automatic check records
LEDGER_KNOWN = {
    '69dfbd8e': 'the variety of 2dc27508, axiomatized differently (ledger row 7; E both ways)',
}


def _load(name, default=None):
    p = data('check', name)
    return json.load(open(p)) if p.exists() else default


def _src_path(src, *parts):
    return data(*parts) if src == '.' else data(src, *parts)


def _match(table, key):
    return next((v for k, v in table.items() if str(key).startswith(k)), None)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--readme', help='README to update between the candidates markers')
    a = ap.parse_args()
    from .core import Corpus, ORDER
    from .data import NONDEG, PROBES, SIZES, sat_base, unpack_probes
    from .offdiag import DIAG, offdiag_gain

    cands = _load('candidates.json')
    profs = {json.dumps(sorted(p['T'])): p for p in _load('profile_candidates.json', [])}
    split = {c['key']: c.get('split', 'not run') for c in _load('split_candidates.json', [])}
    hidden = {c['key']: c.get('definitional') for c in _load('hidden_candidates.json', [])}
    relab = {c['key']: c for c in _load('relabel_candidates.json', [])}
    r1 = (_load('rediscover.json', {}) or {}).get('sources', {})
    dedupe = _load('dedupe_candidates.json', {'classes': []})
    rk = _load('ranking.json', {'candidates': []})
    t5a_rank = {r['key']: i for i, r in enumerate(rk['candidates'], 1)}
    t5a_equiv = {r['key']: r['equivalent_to'] for r in rk.get('excluded_equivalent', [])}
    classical = np.array([not re.match(r'(rand|all2)', name) for name, _ in PROBES])

    score = {c['key']: c.get('score') or 0 for c in cands}
    rep_of, related_of = {}, {}
    for cls in dedupe.get('classes', []):
        rep = max(cls, key=lambda k: score.get(k, 0))
        for k in cls:
            if k != rep: rep_of[k] = rep
        # a partial identification belongs to the variety: every member of the class carries it (N1, clarification)
        hit = next(((k, _match(RELATED, k)) for k in cls if _match(RELATED, k)), None)
        if hit:
            for k in cls:
                related_of[k] = hit[1] if k == hit[0] else f'{hit[1]} (same variety as {hit[0][:8]})'

    rows = []
    for c in cands:
        key, src = c['key'], c['source']
        row = {'key': key, 'source': src, 'laws': c['laws'], 'T': c['T'], 'score': c.get('score'),
               't5a_rank': t5a_rank.get(key), 'known': [], 'flags': [],
               'related': related_of.get(key) or _match(RELATED, key)}
        rpath = _src_path(src, 'results', f'{key}.json')
        res = json.load(open(rpath)) if src != 'pilot' and os.path.exists(rpath) else None
        prof = profs.get(json.dumps(sorted(c['T'])), {})
        spec = prof.get('spectrum') or {}
        row['nondeg_sizes'] = sum(1 for s in spec.values() if (s.get('nondeg') or 0) > 0)
        row['axiom_size'] = int(sum(ORDER[t] for t in c['T']))
        row['record'] = res is not None
        row['works'] = bool(res) and any(x.get('status') == 'proved' for x in res.get('claims', [])) \
            and row['nondeg_sizes'] >= 2
        # identification
        k = _match(LEDGER_KNOWN, key)
        if k: row['known'].append(f'ledger: {k}')
        if t5a_equiv.get(key): row['known'].append(f'equivalent to a standard theory: {t5a_equiv[key]}')
        s = split.get(key, 'not run')
        if s is True: row['known'].append('split: a ·-theory and a ∘-theory side by side (soup.split)')
        elif s is None or s == 'not run': row['flags'].append(f'split {s}')
        if hidden.get(key): row['known'].append('definitional: one operation is a term in the other (soup.hidden)')
        if res and res.get('screened'): row['known'].append(f"V4: {res['screened']}")
        rl = relab.get(key, {})
        for f, word in (('implies', 'implies'), ('fragment_of', 'fragment of'), ('equivalent_to', 'equivalent to')):
            for n in rl.get(f) or []:
                (row['flags'] if '?' in n else row['known']).append(f'soup.relabel: {word} {n}')
        for x in r1.get(src, {}).get('relations', []):
            if x['key'] != key: continue
            text = f"R1: {x['kind']} of {x['entry']} ({x['relabel']})"
            (row['flags'] if x['kind'].endswith('?') else row['known']).append(text)
        if key in rep_of: row['known'].append(f'same variety as {rep_of[key][:8]} (soup.dedupe)')
        # classical models
        base = unpack_probes(sat_base(list(c['T'])))
        cl = np.flatnonzero(base & NONDEG & (SIZES >= 3) & classical)
        row['classical_models'] = len(cl)
        row['classical_example'] = PROBES[cl[0]][0] if len(cl) else None
        row['_res'] = res
        rows.append(row)

    # off-diagonal proved emergent laws, for the gated candidates, one corpus per run
    gated = [r for r in rows if r['record'] and r['works'] and not r['known']]
    for src in sorted({r['source'] for r in gated}):
        C = Corpus(store=_src_path(src, 'corpus'))
        for r in (x for x in gated if x['source'] == src):
            g = offdiag_gain(C, sorted(r['T']))
            gs = set(g.tolist()) if g is not None else set()
            r['offdiag_laws'] = sorted({x['law'] for x in r['_res'].get('claims', [])
                                        if x.get('status') == 'proved' and not DIAG[x['idx']] and x['idx'] in gs})
    for r in rows: r.pop('_res', None)

    def order(r):
        return (not r['offdiag_laws'], r['classical_models'] > 0, r['related'] is not None, -r['nondeg_sizes'],
                r['axiom_size'], -(r['score'] or 0))
    ranked = sorted(gated, key=order)
    for i, r in enumerate(ranked, 1): r['n1_rank'] = i
    known = [r for r in rows if r['known']]
    not_works = [r for r in rows if r['record'] and not r['works'] and not r['known']]
    no_record = [r for r in rows if not r['record']]

    gate = {'pool': len(rows), 'no verification record': len(no_record), 'fails works': len(not_works),
            'identified (known)': len(known), 'enters N1': len(ranked)}
    top_n1 = [r['key'] for r in ranked[:10]]
    top_t5a = [r['key'] for r in rk['candidates'][:10]]
    out = {'gate': gate, 'overlap_top10_with_t5a': len(set(top_n1) & set(top_t5a)),
           'top10_by_run': {s: sum(1 for r in ranked[:10] if r['source'] == s) for s in sorted({r['source'] for r in ranked})},
           't5a_top10_by_run': {s: sum(1 for r in rk['candidates'][:10] if r['source'] == s)
                                for s in sorted({r['source'] for r in rk['candidates'][:10]})},
           'ranked': ranked, 'known': known, 'not_works': not_works, 'no_record': no_record}
    json.dump(out, open(data('check', 'novelty_ranking.json'), 'w'), ensure_ascii=False, indent=1)
    _table(out)
    if a.readme: _readme(out, Path(a.readme))
    print(json.dumps({k: out[k] for k in ('gate', 'overlap_top10_with_t5a', 'top10_by_run', 't5a_top10_by_run')},
                     ensure_ascii=False))
    for r in ranked[:20]:
        print(f"{r['n1_rank']:3d} {r['key'][:8]} {r['source']:10s} offdiag {len(r['offdiag_laws'])} classical "
              f"{r['classical_models']} related {'y' if r['related'] else '-'} sizes {r['nondeg_sizes']} "
              f"axioms {r['axiom_size']} score {r['score']} T5a {r['t5a_rank']} {'; '.join(r['flags'])}")


def _yn(b): return 'yes' if b else 'no'


def _table(out):
    L = ['# Candidates: known, and not known as far as our checks go', '',
         'Generated by `podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes" soup python3 -m soup.novelty` '
         '(PREREGISTRATION.md, N1). "Not known" means: no automatic check, catalogue relation or ledger entry '
         'identifies it, and our literature searches (web, zbMATH) found no source where one was run. Our searches are '
         'weak evidence (REPORT.md, Coverage); nothing here is claimed to be new.', '',
         f"Pool {out['gate']['pool']}: {out['gate']['identified (known)']} known, {out['gate']['enters N1']} not known "
         f"(ranked by N1), {out['gate']['fails works']} failing \"works\", {out['gate']['no verification record']} "
         'without a verification record.', '',
         f"## Not known as far as our checks go ({len(out['ranked'])}), in N1 order", '',
         'Metric (lexicographic): an off-diagonal proved emergent law; no classical model (structured probes, 3+ '
         'elements); not related to a known structure by a partial identification; more sizes with non-degenerate '
         'models; smaller axioms (sum of law orders); verified score.', '',
         '| N1 | key | run | off-diagonal law | classical model | related to | sizes | axiom size | score | T5a | '
         'flags | laws |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in out['ranked']:
        L.append(f"| {r['n1_rank']} | `{r['key'][:8]}` | {r['source']} | "
                 f"{'; '.join(r['offdiag_laws'][:2]) or 'no'}{' …' if len(r['offdiag_laws']) > 2 else ''} | "
                 f"{_yn(r['classical_models'])} | {r['related'] or '-'} | {r['nondeg_sizes']} | {r['axiom_size']} | "
                 f"{r['score']} | {r['t5a_rank'] or '-'} | {'; '.join(r['flags']) or '-'} | {' & '.join(r['laws'])} |")
    L += ['', f"## Known ({len(out['known'])})", '', '| key | run | what it is / how identified | laws |',
          '|---|---|---|---|']
    for r in out['known']:
        L.append(f"| `{r['key'][:8]}` | {r['source']} | {'; '.join(r['known'])} | {' & '.join(r['laws'])} |")
    L += ['', f"## Not passing \"works\" ({len(out['not_works'])})", '',
          'No proved emergent law, or non-degenerate models on fewer than 2 sizes (profile spectrum, 2–5 elements).', '']
    L += [f"- `{r['key'][:8]}` ({r['source']}): sizes {r['nondeg_sizes']}; {' & '.join(r['laws'])}" for r in out['not_works']]
    L += ['', '## Without a verification record', '']
    L += [f"- `{r['key']}` ({r['source']}): {' & '.join(r['laws'])}" for r in out['no_record']]
    target = Path('/notes') if Path('/notes').is_dir() else data('check')
    (target / 'candidates_table.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


START, END = '<!-- candidates:start -->', '<!-- candidates:end -->'


def _readme(out, path):
    """Rewrite the live block of the README (in place: the file may be a bind mount)."""
    import collections
    import datetime
    g = out['gate']
    kinds = collections.Counter()
    for r in out['known']:
        first = r['known'][0]
        kinds[('split' if first.startswith('split') else 'definitional' if first.startswith('definitional')
               else 'same variety as another candidate' if 'soup.dedupe' in first
               else 'related to a named or catalogued structure' if first.startswith(('soup.relabel', 'R1'))
               else 'identified by hand (ledger)' if first.startswith('ledger') else first.split(':')[0])] += 1
    when = datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %Y, %H:%M UTC')
    B = [START, f'*Regenerated by `soup.novelty` after each run\'s checks; last update {when}. '
         'Full tables: [`notes/candidates_table.md`](notes/candidates_table.md).*', '',
         f"The candidate pool holds the top 20 non-fragments of each run: {g['pool']} theories. "
         f"**{g['identified (known)']} are known**: "
         + ', '.join(f'{n} {k}' for k, n in kinds.most_common()) + '. '
         f"**{g['enters N1']} are not known as far as our checks go**, and are ranked below. "
         f"{g['fails works']} fail \"works\" and {g['no verification record']} have no verification record.", '',
         '**Metric (N1, preregistered).** A candidate enters only if it works, meaning it has a proved emergent law and '
         'non-degenerate models on two or more sizes, and no check identifies it. It is then ordered by:',
         '1. a proved emergent law off the diagonal, meaning not just a statement about x·x and x∘x;',
         '2. no model among the classical constructions: affine, group-derived, lattices, rings;',
         '3. no partial identification by hand;',
         '4. more sizes with non-degenerate models;',
         '5. smaller axioms;',
         '6. verified score.',
         '', '"Not known" is not "new". It means our checks and catalogue found nothing. Web searches have been run only '
         'for some top entries, and they are weak evidence.', '',
         '| N1 | theory | run | off-diagonal law | classical model | partly known as | sizes | T5a rank |',
         '|---|---|---|---|---|---|---|---|']
    for r in out['ranked'][:10]:
        B.append(f"| {r['n1_rank']} | `{r['key'][:8]}`: {' & '.join(r['laws'])} | {r['source']} | "
                 f"{r['offdiag_laws'][0] if r['offdiag_laws'] else 'no'} | {_yn(r['classical_models'])} | "
                 f"{r['related'] or '-'} | {r['nondeg_sizes']} | {r['t5a_rank'] or '-'} |")
    B.append(END)
    text = path.read_text(encoding='utf-8')
    if START not in text or END not in text:
        print(f'{path}: markers not found, README not changed'); return
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(head + '\n'.join(B) + tail)
    print(f'{path}: live candidates block rewritten')


if __name__ == '__main__':
    main()
