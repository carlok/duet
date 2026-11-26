"""What earlier runs already know, for the searcher's skips (arm 'fusion4', run X7, 23 Nov 2026).

    python -m soup.known build --out /data/x7 [--notes /notes]   -> known_library.json, seen_before.json

Two files, built once before a run, from the shared data root (SOUP_DATA, normally /data):
- known_library.json: theories to stay away from, each as law indices, under all 8 relabellings (soup.relabel).
  kind 'known': the catalogue (soup.catalogue: the 10 named theories of T3 and 3 more) and every candidate identified
  in the ledger (notes/rediscovery.md, rows whose first cell names candidate keys). The searcher skips a theory that is
  a fragment of one of them or a subvariety of one, on the corpus.
  kind 'candidate': every earlier candidate (check/candidates.json). The searcher skips only a theory equivalent to
  one of them on the corpus (fragment and subvariety at once): a strengthening of an unidentified candidate is new.
- seen_before.json: the theory keys (soup.duality.theory_key) of everything earlier runs pushed to their queue or
  verified, over every run directory. The searcher never pushes one of them again.

Known (the class Library) works on bit vectors: for a theory T with corpus-implied laws imp_T,
  subvariety of K   imp_T holds every law of K
  fragment of K     every law of T holds in all corpus models of K (the law vector implied(K))
Both are guesses from the corpus, as the lattice skip is; the corpus over-approximates implication, so a skip can be
wrong in the direction of skipping too much, never of keeping a known theory.
"""
import argparse
import glob
import json
import os
import re

import numpy as np

from .paths import data

# earlier runs; the output directory itself and missing directories are skipped (X8 added x4a and x7, 24 Nov 2026)
RUN_DIRS = ['.', 't4-prior', 't4-noprior', 'x1', 'x2', 'x3', 'x4', 'x4a', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10', 'x11', 'x12-f5', 'x12-f6']


def _relabelled(T):
    from .relabel import relabellings, relabel_law
    out = set()
    for _, r in relabellings():
        L = [relabel_law(t, r) for t in T]
        if None not in L: out.add(tuple(sorted(set(L))))
    return sorted(out)


def build(out, notes='/notes', root=None):
    from .catalogue import KNOWN
    from .named import law_index
    root = root or data()
    lib = []
    for name, e in KNOWN.items():
        T = [law_index(s.replace(' ', '')) for s in e['laws']]
        if None in T: continue
        lib += [{'name': name, 'kind': 'known', 'T': list(R)} for R in _relabelled(T)]
    cand = json.load(open(os.path.join(root, 'check', 'candidates.json')))
    by8 = {c['key'][:8]: c for c in cand}
    lp = os.path.join(notes, 'rediscovery.md')
    ledger = open(lp).read() if os.path.exists(lp) else ''          # no ledger (tests): catalogue only
    ident = set()
    for line in ledger.splitlines():
        m = re.match(r'\| \d+ \| ([^|]*)\|', line)
        if m: ident |= {k for k in re.findall(r'`([0-9a-f]{8})`', m.group(1)) if k in by8}
    for k in sorted(ident):
        lib += [{'name': f'ledger:{k}', 'kind': 'known', 'T': list(R)} for R in _relabelled(by8[k]['T'])]
    for c in cand:
        if c['key'][:8] in ident: continue
        lib += [{'name': f"candidate:{c['key'][:8]}", 'kind': 'candidate', 'T': list(R)} for R in _relabelled(c['T'])]
    seen = set()
    for d in RUN_DIRS:
        base = root if d == '.' else os.path.join(root, d)
        if not os.path.isdir(base) or os.path.realpath(base) == os.path.realpath(out): continue
        seen |= {os.path.basename(p) for p in glob.glob(os.path.join(base, 'queue', 'seen', '*'))}
        seen |= {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(base, 'results', '*.json'))}
    os.makedirs(out, exist_ok=True)
    json.dump(lib, open(os.path.join(out, 'known_library.json'), 'w'))
    json.dump(sorted(seen), open(os.path.join(out, 'seen_before.json'), 'w'))
    nk = sum(e['kind'] == 'known' for e in lib)
    print(f'library: {nk} known entries (catalogue + {len(ident)} ledger candidates, 8 relabellings), '
          f'{len(lib) - nk} candidate entries; seen before: {len(seen)} keys')


class Library:
    """Vectorised known/candidate tests against a corpus (see the module docstring)."""

    def __init__(self, C, path):
        from .core import NL
        self.C, self.NL = C, NL
        lib = json.load(open(os.path.join(path, 'known_library.json')))
        self.names = [e['name'] for e in lib]
        self.known = np.array([e['kind'] == 'known' for e in lib])
        self.Ts = [e['T'] for e in lib]
        self.idx = np.concatenate([np.array(T, np.int64) for T in self.Ts])
        self.starts = np.cumsum([0] + [len(T) for T in self.Ts])[:-1]
        self.sizes = np.array([len(T) for T in self.Ts])
        self.refresh()

    def refresh(self):
        """Corpus models of each library theory: implied(K) as a bit matrix, laws by entries (packed)."""
        E = len(self.Ts)
        M = np.zeros((self.NL, E), bool); self.has_models = np.zeros(E, bool)
        for j, T in enumerate(self.Ts):
            imp = self.C.implied(T)
            if imp is not None: M[:, j] = imp; self.has_models[j] = True
        self.F = np.packbits(M, axis=1)          # NL x ceil(E/8)

    def classify(self, T, imp):
        """'known' if T is a fragment or a subvariety of a known entry; 'candidate' if equivalent to an earlier
        candidate; None otherwise. imp: corpus-implied law vector of T."""
        E = len(self.Ts)
        sub = np.add.reduceat(imp[self.idx].astype(np.int32), self.starts) == self.sizes          # T implies K
        frag = np.bitwise_and.reduce(self.F[list(T)], axis=0)
        frag = np.unpackbits(frag)[:E].astype(bool) & self.has_models                             # K implies T
        if ((sub | frag) & self.known).any(): return 'known'
        if (sub & frag & ~self.known).any(): return 'candidate'
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['build'])
    ap.add_argument('--out', required=True); ap.add_argument('--notes', default='/notes')
    a = ap.parse_args()
    build(a.out, a.notes)


if __name__ == '__main__':
    main()
