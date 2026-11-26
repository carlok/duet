"""F1 (PREREGISTRATION.md, 24 Nov 2026): families of verified theories, and emerging patterns.

    podman run --rm -v "$PWD/work:/data" -v "$PWD/notes:/notes:ro" soup python3 -m soup.taxonomy build --confirm --jobs 8
    podman run --rm -v "$PWD/work:/data:ro" -v "$PWD/README.md:/repo/README.md" -v "$PWD/docs:/repo/docs" \\
        soup python3 -m soup.taxonomy report --readme /repo/README.md --docs /repo/docs/families.md

Every verified theory gets one primary family, by the first rule that matches: disguise (screened in stage a), known
(a proved catalogue relation in check/rediscover.json, or a ledger identification), no synergy, diagonal (a proved
one-variable emergent law), argument-ignoring (implies an offdiag.IGNORE law on the corpus), structured. Structured
theories are labelled by their reduct signature: which of 11 one-operation properties hold for · and for ∘ (22 laws,
closed under the 8 relabellings), in every model in the union of all runs' corpora; the label is the least one over
the 8 relabellings. `--confirm` asks E for each such property of a structured theory (10 s, 200,000 clauses).
Not a search component: post hoc only (rule 6 does not apply, no LLM anywhere).
"""
import argparse
import collections
import glob
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

RUNS = ['.', 't4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10', 'x11']
PRIMARY = ['disguise', 'known', 'no synergy', 'diagonal', 'argument-ignoring', 'structured']
PROPS = [('comm', 'x · y = y · x'), ('assoc', '(x · y) · z = x · (y · z)'), ('idem', 'x · x = x'),
         ('const-sq', 'x · x = y · y'), ('sq-right-id', 'x · (y · y) = x'), ('sq-left-id', '(y · y) · x = x'),
         ('left-inv', 'x · (x · y) = y'), ('right-inv', '(y · x) · x = y'), ('flex', 'x · (y · x) = (x · y) · x'),
         ('x(yz)=xy', 'x · (y · z) = x · y'), ('(xy)z=yz', '(x · y) · z = y · z')]
START, END = '<!-- families:start -->', '<!-- families:end -->'


def _prop_laws():
    from .named import law_index
    out = {}
    for name, s in PROPS:
        out[law_index(s)] = ('·', name)
        out[law_index(s.replace('·', '∘'))] = ('∘', name)
    assert None not in out and len(out) == 22
    return out


PL = None          # law index -> (op, property name), built on first use
RL = None          # per relabelling: law index -> image, for the 22 property laws


def _init():
    global PL, RL
    if PL is not None: return
    from .relabel import relabellings, relabel_law
    PL = _prop_laws()
    RL = [{i: relabel_law(i, r) for i in PL} for _, r in relabellings()]
    assert all(set(m.values()) == set(PL) for m in RL), 'property laws not closed under relabelling'


def label(S):
    """A readable label of a set of property laws, e.g. '·: TSQ | ∘: idem'."""
    _init()
    order = [n for n, _ in PROPS]
    parts = []
    for op in '·∘':
        names = sorted((PL[i][1] for i in S if PL[i][0] == op), key=order.index)
        if 'comm' in names and 'left-inv' in names:          # commutative + left involutive: totally symmetric
            names = ['TSQ'] + [n for n in names if n not in ('comm', 'left-inv', 'right-inv')]
        parts.append(f'{op}: {", ".join(names) or "-"}')
    return ' | '.join(parts)


def canonical_label(S):
    """The least label over the 8 relabellings (r maps a law of T to the corresponding law of r(T))."""
    _init()
    return min(label({m[i] for i in S}) for m in RL)


def signature(imp):
    """The property laws among the corpus-implied laws (bool vector over all laws)."""
    _init()
    return sorted(i for i in PL if imp[i])


_FAM = {}


def family_of(imp):
    """The structured-family label of a corpus-implied law vector, canonical under the 8 relabellings; cached per
    signature. Arm fusion6 uses it in the search (one corpus, no E confirmation), so it can differ from F1's label."""
    s = tuple(signature(imp))
    if s not in _FAM: _FAM[s] = canonical_label(s)
    return _FAM[s]


def chao1(counts):
    """Chao1 richness estimate from the abundance of each class. S + f1^2 / (2 f2); bias-corrected
    S + f1 (f1 - 1) / 2 when f2 = 0."""
    counts = [c for c in counts if c > 0]
    S, f1, f2 = len(counts), sum(c == 1 for c in counts), sum(c == 2 for c in counts)
    return S + (f1 * f1 / (2 * f2) if f2 else f1 * (f1 - 1) / 2)


def primary(r, imp, known_keys, ledger_keys):
    """(primary family, subtype) of one verified theory r (a results/*.json dict)."""
    from .offdiag import IGNORE, ONEVAR
    if r.get('screened'): return 'disguise', str(r['screened'])
    k = r['key']
    if k in known_keys: return 'known', known_keys[k]
    if k[:8] in ledger_keys: return 'known', 'ledger'
    proved = [c for c in r.get('claims', []) if c.get('status') == 'proved' and c.get('idx') is not None]
    if not proved: return 'no synergy', ''
    if any(ONEVAR[int(c['idx'])] for c in proved): return 'diagonal', ''
    if imp is not None and (imp & IGNORE).any(): return 'argument-ignoring', ''
    return 'structured', ''


# ---- data

def union_corpus(data='/data'):
    """One Corpus over the base probes and every corpus directory (deduplicated by structure key); read only."""
    from .core import Corpus
    C = Corpus()
    for d in [os.path.join(data, 'corpus')] + sorted(glob.glob(os.path.join(data, '*', 'corpus'))):
        if os.path.isdir(d): C.store = Path(d); C.refresh()
    C.store = None
    return C


def known_relations(data='/data'):
    """key -> first catalogue entry (catalogue order) with an E-proved relation (fragment, subvariety, equivalent)."""
    from .catalogue import KNOWN
    order = list(KNOWN)
    p = os.path.join(data, 'check', 'rediscover.json')
    best = {}
    if not os.path.exists(p): return best
    for src in json.load(open(p))['sources'].values():
        for rel in src['relations']:
            if rel['kind'] not in ('fragment', 'subvariety', 'equivalent'): continue
            k, e = rel['key'], rel['entry']
            if k not in best or order.index(e) < order.index(best[k]): best[k] = e
    return best


def ledger_keys(notes='/notes'):
    p = os.path.join(notes, 'rediscovery.md')
    if not os.path.exists(p): return set()
    rows = [l for l in open(p).read().splitlines() if re.match(r'\| \d+ \|', l)]
    return set(re.findall(r'`([0-9a-f]{8})', '\n'.join(rows)))


def results(data='/data'):
    for d in RUNS:
        base = data if d == '.' else os.path.join(data, d)
        for f in sorted(glob.glob(os.path.join(base, 'results', '*.json'))):
            try: r = json.load(open(f))
            except Exception: continue
            if not r.get('T'): continue
            yield d, r


def build(data='/data', notes='/notes', confirm=False, jobs=8, secs=10):
    _init()
    t0 = time.time()
    C = union_corpus(data); print(f'union corpus: {len(C)} found structures ({time.time() - t0:.0f} s)', flush=True)
    KR, LK = known_relations(data), ledger_keys(notes)
    out = []
    for d, r in results(data):
        T = sorted({int(t) for t in r['T']})
        imp = C.implied(T)
        fam, sub = primary(r, imp, KR, LK)
        sig = signature(imp) if imp is not None else None
        proved = sorted({int(c['idx']) for c in r.get('claims', []) if c.get('status') == 'proved' and c.get('idx') is not None})
        out.append({'run': d, 'key': r['key'], 'T': T, 't_done': r.get('t_done'), 'primary': fam, 'subtype': sub,
                    'sig': sig, 'family': canonical_label(sig) if sig is not None else '(no corpus model)',
                    'proved': proved})
    print(f'{len(out)} theories classified ({time.time() - t0:.0f} s)', flush=True)
    cache_p = os.path.join(data, 'check', 'families_e.json')
    cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    if confirm:
        from .provers import prove_e
        todo = sorted({(tuple(t['T']), i) for t in out if t['primary'] == 'structured' and t['sig']
                       for i in t['sig'] if i not in t['T']})
        todo = [(T, i) for T, i in todo if json.dumps([list(T), i]) not in cache]
        print(f'E: {len(todo)} (theory, property) pairs to check', flush=True)
        done = 0
        with ThreadPoolExecutor(jobs) as ex:
            fut = {ex.submit(prove_e, list(T), i, 200_000, secs): (T, i) for T, i in todo}
            for f in as_completed(fut):
                T, i = fut[f]
                try: st = f.result()['status']
                except Exception as e: st = f'error {e}'
                cache[json.dumps([list(T), i])] = st; done += 1
                if done % 500 == 0:
                    json.dump(cache, open(cache_p, 'w')); print(f'  E {done}/{len(todo)}', flush=True)
        json.dump(cache, open(cache_p, 'w'))
    for t in out:
        if t['primary'] == 'structured' and t['sig']:
            t['e'] = {str(i): ('axiom' if i in t['T'] else cache.get(json.dumps([t['T'], i]))) for i in t['sig']}
    res = {'computed': time.strftime('%d %b %Y, %H:%M UTC', time.gmtime()), 'corpus': len(C), 'theories': out}
    json.dump(res, open(os.path.join(data, 'check', 'families.json'), 'w'))
    print(f'wrote check/families.json ({time.time() - t0:.0f} s)')
    return res


# ---- report

def _name(d): return 'root' if d == '.' else d


def analyse(res, data='/data'):
    from .data import LAWS
    from .relabel import relabellings, relabel_law
    from .funnel import _evals
    th = [t for t in res['theories']]
    runs = [d for d in RUNS if any(t['run'] == d for t in th)]
    by_run = {d: [t for t in th if t['run'] == d] for d in runs}
    prim = {d: collections.Counter(t['primary'] for t in by_run[d]) for d in runs}
    # structured families: new and emerging, per run
    S = [t for t in th if t['primary'] == 'structured']
    fam_run = {d: collections.Counter(t['family'] for t in by_run[d] if t['primary'] == 'structured') for d in runs}
    flags, seen, before = {}, set(), collections.Counter()
    n_before = 0
    for d in runs:
        n = len(by_run[d])
        for f, c in fam_run[d].items():
            if f not in seen: flags.setdefault(f, []).append(f'new in {_name(d)}')
            elif c >= 10 and n_before and c / n >= 2 * before[f] / n_before: flags.setdefault(f, []).append(f'emerging in {_name(d)}')
        seen |= set(fam_run[d]); before.update(fam_run[d]); n_before += n
    # proved emergent laws up to relabelling
    rels = [r for _, r in relabellings()]
    canon_cache = {}
    def canon(i):
        if i not in canon_cache:
            canon_cache[i] = min(j for j in (relabel_law(i, r) for r in rels) if j is not None)
        return canon_cache[i]
    law_run = {d: collections.Counter(c for t in by_run[d] for c in {canon(i) for i in t['proved']}) for d in runs}
    lflags, seen, before, n_before = {}, set(), collections.Counter(), 0
    for d in runs:
        n = len(by_run[d])
        for l, c in law_run[d].items():
            if l not in seen: lflags.setdefault(l, []).append(f'new in {_name(d)}')
            elif l in seen and c >= 10 and n_before and c / n >= 2 * before[l] / n_before: lflags.setdefault(l, []).append(f'emerging in {_name(d)}')
        seen |= set(law_run[d]); before.update(law_run[d]); n_before += n
    # accumulation curve, at each run's end
    curve, cnt, cum_v, cum_0 = [], collections.Counter(), 0, 0
    for d in runs:
        for t in sorted(by_run[d], key=lambda t: t.get('t_done') or 0):
            if t['primary'] == 'structured': cnt[t['family']] += 1
        cum_v += len(by_run[d]); cum_0 += _evals(data if d == '.' else os.path.join(data, d))
        curve.append({'run': _name(d), 'verified': cum_v, 'level0': cum_0, 'families': len(cnt),
                      'chao1': round(chao1(cnt.values()), 1)})
    # E confirmation
    e = collections.Counter(v for t in S for v in (t.get('e') or {}).values())
    return dict(runs=runs, by_run=by_run, prim=prim, fam_run=fam_run, flags=flags, law_run=law_run, lflags=lflags,
                curve=curve, e=e, laws=LAWS, S=S, total=len(th))


def _pct(a, b): return f'{100 * a / b:.1f}%' if b else '-'


def readme_block(A, when):
    tot = collections.Counter(); [tot.update(A['prim'][d]) for d in A['runs']]
    last = A['runs'][-1]; nl = len(A['by_run'][last])
    out = [START, f'*Regenerated by `soup.taxonomy` (F1, preregistered) after each run\'s checks; last update {when}. '
           f'Details: [`docs/families.md`](docs/families.md).*', '',
           f'| family | theories | share | in {_name(last)} |', '|---|---:|---:|---:|']
    for p in PRIMARY:
        out.append(f'| {p} | {tot[p]:,} | {_pct(tot[p], A["total"])} | {_pct(A["prim"][last][p], nl)} |')
    fam = collections.Counter(t['family'] for t in A['S'])
    c = A['curve'][-1]
    out += ['', f'**Structured families:** {c["families"]} distinct, and the count is still rising. Chao1 gives '
            f'{c["chao1"]:.0f}, but only as a descriptive index: the search skips what it has seen, so the sample is '
            f'biased and Chao1 does not estimate the total ([notes/metafield.md](notes/metafield.md)). The largest:', '']
    for f, n in fam.most_common(5):
        fl = '; '.join(A['flags'].get(f, []))
        out.append(f'- `{f}`: {n} ({_pct(n, len(A["S"]))} of structured){" — " + fl if fl else ""}')
    new_last = sum(1 for f, fl in A['flags'].items() if f'new in {_name(last)}' in fl)
    out += ['', f'{_name(last)} added {new_last} new structured families. Properties are corpus-implied; '
            f'E confirmed {_pct(A["e"]["proved"] + A["e"]["axiom"], sum(A["e"].values()))} of them.', END]
    return '\n'.join(out)


def docs_page(A, when, res):
    R = A['runs']; nm = [_name(d) for d in R]
    L = ['# Families of verified theories, and emerging patterns', '',
         f'*Generated by `soup.taxonomy` (PREREGISTRATION.md, F1) on {when}, over {A["total"]:,} verified theories and '
         f'a union corpus of {res["corpus"]:,} found structures. Not a search component: computed after the runs.*', '',
         'Each verified theory gets one **primary family**, by the first rule that matches: a disguise screened by the '
         'verifier; known (a proved relation to a catalogue entry, or identified in the ledger); no synergy; diagonal (a '
         'one-variable emergent law); argument-ignoring (X4\'s attractor); and the rest, **structured**. A structured '
         'theory is labelled by its *reduct signature*: which of 11 properties hold for each operation, in every model '
         'of it in the corpus, read up to the 8 relabellings. TSQ is a totally symmetric quasigroup (commutative and '
         'x·(x·y) = y).', '', '## Primary families by run (share of the run\'s verified theories)', '',
         '| family | ' + ' | '.join(nm) + ' |', '|---|' + '---:|' * len(R)]
    for p in PRIMARY:
        L.append(f'| {p} | ' + ' | '.join(_pct(A['prim'][d][p], len(A['by_run'][d])) for d in R) + ' |')
    L.append('| verified | ' + ' | '.join(f'{len(A["by_run"][d]):,}' for d in R) + ' |')
    fam = collections.Counter(t['family'] for t in A['S'])
    L += ['', '## Structured families (top 30), theories per run', '',
          '| family | all | ' + ' | '.join(nm) + ' | flags |', '|---|---:|' + '---:|' * len(R) + '---|']
    for f, n in fam.most_common(30):
        L.append(f'| `{f.replace("|", chr(92) + "|")}` | {n} | ' + ' | '.join(str(A['fam_run'][d][f] or '') for d in R) + f' | {"; ".join(A["flags"].get(f, []))} |')
    L += ['', f'{len(fam)} structured families in all; {sum(1 for v in fam.values() if v == 1)} seen once. '
          '"New": no earlier run has it. "Emerging": at least 10 theories in the run and at least twice its share in all '
          'earlier runs together.', '',
          '## Proved emergent laws (top 25, up to relabelling), theories per run', '',
          '| law | all | ' + ' | '.join(nm) + ' | flags |', '|---|---:|' + '---:|' * len(R) + '---|']
    lt = collections.Counter(); [lt.update(A['law_run'][d]) for d in R]
    for l, n in lt.most_common(25):
        L.append(f'| {A["laws"][l]} | {n} | ' + ' | '.join(str(A['law_run'][d][l] or '') for d in R) + f' | {"; ".join(A["lflags"].get(l, []))} |')
    flagged = [(l, fl) for l, fl in A['lflags'].items() if l not in dict(lt.most_common(25))]
    if flagged:
        L += ['', 'Other flagged laws: ' + '; '.join(f'{A["laws"][l]} ({", ".join(fl)})' for l, fl in
                                                    sorted(flagged, key=lambda x: -lt[x[0]])[:15]) + '.']
    L += ['', '## The accumulation curve', '',
          'Distinct structured families as verified theories accumulate, run by run, with the level 0 reached at each '
          'run\'s end. If the count still rises steeply, the search has not exhausted what it can reach. (Level 0 here '
          'leaves out x4a\'s 0.17M evaluations, whose results are not used; the funnel counts them.)', '',
          'Chao1 is S + f1²/(2 f2), computed from the families seen once (f1) and twice (f2). It estimates a total only '
          'when the sample is unbiased and drawn from a fixed population. Here neither holds. The fusion arms skip '
          'known theories and every theory seen before, and the arms change from run to run. So the column is a '
          'descriptive index of how many families are still singletons, not an estimate of how many exist. STADS '
          '(Böhme 2018) raises the same problem for fuzzers, and Hajič and Moss (2025) show that the bounds stay loose '
          'while new items keep arriving at a steady rate ([notes/metafield.md](../notes/metafield.md)).', '',
          '| after | verified | level 0 | families | Chao1 |', '|---|---:|---:|---:|---:|']
    for c in A['curve']:
        L.append(f'| {c["run"]} | {c["verified"]:,} | {c["level0"]:,} | {c["families"]} | {c["chao1"]:.0f} |')
    e = A['e']; tot = sum(e.values())
    L += ['', '## Evidence', '',
          f'Structured theories carry {tot:,} corpus-implied properties: {e["axiom"]:,} are axioms, E proves '
          f'{e["proved"]:,}, E finds {e["countersatisfiable"]:,} false (the corpus was too thin), and '
          f'{tot - e["axiom"] - e["proved"] - e["countersatisfiable"]:,} are unknown within 10 s. Labels use the corpus '
          'view; the false ones mark how far it over-approximates.', '',
          '## Caveats', '',
          '- Corpus implication over-approximates implication: a signature can be too rich (see the E counts).',
          '- Eleven properties name only what they list: two theories in one family can still differ a lot.',
          '- "Known" relies on our catalogue and ledger, not on the literature.',
          '- Runs differ in arm and filters, so shares across runs compare search strategies as much as regions.', '']
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['build', 'report'])
    ap.add_argument('--confirm', action='store_true'); ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--notes', default='/notes'); ap.add_argument('--readme'); ap.add_argument('--docs')
    a = ap.parse_args()
    if a.cmd == 'build':
        build(notes=a.notes, confirm=a.confirm, jobs=a.jobs); return
    res = json.load(open('/data/check/families.json'))
    A = analyse(res); when = time.strftime('%d %b %Y, %H:%M UTC', time.gmtime())
    b = readme_block(A, when); print(b)
    if a.readme:
        p = Path(a.readme); t = p.read_text()
        i, j = t.index(START), t.index(END) + len(END)
        p.write_text(t[:i] + b + t[j:])
    if a.docs: Path(a.docs).write_text(docs_page(A, when, res))


if __name__ == '__main__':
    main()
