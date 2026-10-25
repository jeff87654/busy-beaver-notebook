"""Lifecycle rules after C3 (context 1::l left of the 21/20 token); r = 2 + 3q."""
import sys, time, traceback
from common import *
from shapes import *
import mexp
U3 = (0, 1) * 3
U6 = (0, 1) * 6
R = accr(2, 'q', U3)
ITEMS = {
 # STAGE: [.., 21, 1^(k+2), 0, 1, a=0] r  -->+  [.., 21, 1^k, 0, 1, a=2r+2] 2
 'STAGE': (K(R, tok(0), tok(1) + tok(0) + list(Z) * 2 + [run(Z, k=1)] + tok(21)),
           K(accr(2), tok(6, 'q', U6), tok(1) + tok(0) + [run(Z, k=1)] + tok(21)), ()),
 # ENDA: [.., 21, 1, 0, 1, a=0] r  -->+  [.., 20, 1, a=2r+2] 2
 'ENDA': (K(R, tok(0), tok(1) + tok(0) + tok(1) + tok(21)),
          K(accr(2), tok(6, 'q', U6), tok(1) + tok(20)), ()),
 # ENDB: [.., 20, 1, a=0] r  -->+  [.., 16, 2r+3, a=1] 2
 'ENDB': (K(R, tok(0), tok(1) + tok(20)),
          K(accr(2), tok(1), tok(7, 'q', U6) + tok(16)), ()),
}
if __name__ == '__main__':
    names = sys.argv[2:] or list(ITEMS)
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name in names:
        s, t, pos = ITEMS[name]
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
            g = mexp.Gen(name)
            rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
            lemmas.extend(g.lemmas)
            print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), flush=True)
        except Exception as e:
            print('%s FAILED: %r' % (name, e), flush=True)
            traceback.print_exc(limit=3)
    text = header('life') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(sys.argv[1], 'w', newline='\n').write(text)
