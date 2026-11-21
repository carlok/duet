"""Parse laws written with · and ∘ and find them in the soup."""
import sys; sys.path.insert(0, '/home/claude/soup')
import pickle
from laws import canon_vars
meta = pickle.load(open('/home/claude/soup/meta.pkl', 'rb'))
KEY = {}
for i, (L, R) in enumerate(meta['law_trees']):
    KEY[min(repr(canon_vars(L, R)), repr(canon_vars(R, L)))] = i
def parse(s):
    s = s.replace(' ', ''); pos = [0]
    def atom():
        if s[pos[0]] == '(':
            pos[0] += 1; t = expr(); pos[0] += 1; return t
        v = 'xyzwuv'.index(s[pos[0]]); pos[0] += 1; return ('v', v)
    def expr():
        t = atom()
        while pos[0] < len(s) and s[pos[0]] in '·∘':
            op = 'f' if s[pos[0]] == '·' else 'g'; pos[0] += 1
            t = (op, t, atom())
        return t
    return expr()
def law_index(text):
    l, r = text.split('=')
    L, R = parse(l), parse(r)
    return KEY.get(min(repr(canon_vars(L, R)), repr(canon_vars(R, L))))
NAMED = {
  'lattice': ['(x·y)·z = x·(y·z)', '(x∘y)∘z = x∘(y∘z)', 'x·y = y·x', 'x∘y = y∘x', 'x·(x∘y) = x', 'x∘(x·y) = x'],
  'dimonoid': ['(x·y)·z = x·(y·z)', '(x·y)·z = x·(y∘z)', '(x∘y)·z = x∘(y·z)', '(x·y)∘z = x∘(y∘z)', '(x∘y)∘z = x∘(y∘z)'],
}
if __name__ == '__main__':
    for name, ls in NAMED.items():
        print(name, [law_index(t) for t in ls])
