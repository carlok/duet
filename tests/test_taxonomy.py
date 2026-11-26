"""F1 (soup.taxonomy): primary families, reduct signatures up to relabelling, Chao1."""
from soup.core import Corpus
from soup.named import law_index
from soup.paths import data
from soup.relabel import relabellings, relabel_law
from soup.taxonomy import canonical_label, chao1, primary, signature, label

C = Corpus(store=data('corpus'))
C38 = ['x · (x · y) = y', '(x · y) · y = x', 'x ∘ (x · y) = x ∘ y', '(x · x) ∘ (x ∘ x) = x', '(x · (x · x)) ∘ x = x']


def T(ls): return sorted(law_index(s.replace(' ', '')) for s in ls)


def test_3818b88f_is_a_tsq_family():
    t = T(C38); imp = C.implied(t)
    lab = canonical_label(signature(imp))
    assert 'TSQ' in lab and 'idem' in lab


def test_relabelled_twin_same_family():
    t = T(C38)
    for _, r in relabellings():
        t2 = sorted(relabel_law(i, r) for i in t)
        assert canonical_label(signature(C.implied(t2))) == canonical_label(signature(C.implied(t)))


def test_family_of_matches_the_label_and_caches():
    from soup.taxonomy import _FAM, family_of
    imp = C.implied(T(C38))
    assert family_of(imp) == canonical_label(signature(imp))
    n = len(_FAM); family_of(imp)
    assert len(_FAM) == n                          # the second call is served from the cache


def test_label_reads():
    S = T(['x · y = y · x', 'x · (x · y) = y', 'x ∘ x = x'])
    assert label(S) == '·: TSQ | ∘: idem'


def test_primary_rules():
    base = {'key': 'ab' * 8, 'claims': [{'status': 'proved', 'idx': law_index('x·x=x')}]}
    assert primary(dict(base, screened='split'), None, {}, set())[0] == 'disguise'
    assert primary(base, None, {'ab' * 8: 'lattice'}, set()) == ('known', 'lattice')
    assert primary(base, None, {}, {'abababab'})[0] == 'known'
    assert primary(dict(base, claims=[]), None, {}, set())[0] == 'no synergy'
    assert primary(base, None, {}, set())[0] == 'diagonal'          # x·x = x is one-variable
    off = dict(base, claims=[{'status': 'proved', 'idx': law_index('x·y=y·x')}])
    assert primary(off, None, {}, set())[0] == 'structured'


def test_chao1():
    assert chao1([5, 3, 2, 1, 1]) == 5 + 4 / 2
    assert chao1([4, 1, 1, 1]) == 4 + 3
