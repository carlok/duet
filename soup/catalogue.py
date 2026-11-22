"""Catalogue of known two-operation structures for the rediscovery analysis R1 (PREREGISTRATION.md, R1).

Fixed on 22 Nov 2026 before R1 was computed. Laws of order <= 4 only (the search's law table). Never used by the
search or the score (rule 6): only by the post hoc analysis `soup.rediscover`.

Each entry: laws (as in soup.named), the source checked for its axioms, and `post_hoc` = True when the entry was
added because one of our own candidates turned out to be it (reported separately).

The first 10 are soup.calib.NAMED (T3, preregistered), copied unchanged. Added for R1, sources checked 22 Nov 2026:
- doppelsemigroup: both operations associative and mutually interassociative. Zhuchok, *Relatively free
  doppelsemigroups* (2018, Zbl 1437.08001, axioms D1, D2 in the review); the same pair of laws defines
  interassociative semigroups (Boyd, Gould, Nelson 1997, Zbl 0915.20030).
- weakly associative lattice (trellis): Fried and Graetzer, Colloq. Math. 27 (1973) 215-221 (Zbl 0325.06004), axioms
  as quoted in the Mizar article LATWAL_1 (Sawicki, Grabowski 2021): idempotent, commutative, and the two weak
  associative laws; absorption follows.
- Delta-bijective pair: (x,y) -> (xy, yx) bijective with its dual operation as the second operation. Bonatto,
  Kinyon, Stanovsky, Vojtechovsky, arXiv:1910.02148, Section 2.5, Lemma 2.10; idea credited to Rump, Adv. Math.
  193 (2005). post_hoc: found because candidate 10c98c4b contains it.
Dropped: quasilattices (Plonka 1967): their axioms need distributivity, of order 5.
"""
from .calib import NAMED

KNOWN = {name: {'laws': list(laws), 'source': 'soup.calib.NAMED (T3, preregistered)', 'post_hoc': False}
         for name, laws in NAMED.items()}
KNOWN.update({
    'doppelsemigroup': {
        'laws': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', '(x·y)∘z = x·(y∘z)', '(x∘y)·z = x∘(y·z)'],
        'source': 'Zhuchok 2018 (Zbl 1437.08001); Boyd, Gould, Nelson 1997 (Zbl 0915.20030)', 'post_hoc': False},
    'weakly associative lattice': {
        'laws': ['x·x = x', 'x∘x = x', 'x·y = y·x', 'x∘y = y∘x', '((x·z)∘(y·z))∘z = z', '((x∘z)·(y∘z))·z = z'],
        'source': 'Fried, Graetzer, Colloq. Math. 27 (1973) (Zbl 0325.06004); Mizar LATWAL_1', 'post_hoc': False},
    'Delta-bijective pair': {
        'laws': ['(x·y)∘(y·x) = x', '(x∘y)·(y∘x) = x'],
        'source': 'Bonatto, Kinyon, Stanovsky, Vojtechovsky, arXiv:1910.02148, Lemma 2.10; Rump 2005',
        'post_hoc': True},
})


def laws_of(name):
    from .named import law_index
    return sorted(law_index(s.replace(' ', '')) for s in KNOWN[name]['laws'])
