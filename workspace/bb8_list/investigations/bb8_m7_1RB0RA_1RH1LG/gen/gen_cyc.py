import sys, time, traceback
from common import *
from shapes import *
from gen_all import KB, U3
import mexp
c, a1, a2 = '110', '10', '1010'
def to_stream(segs):
    out = []
    for seg in reversed(segs):
        if isinstance(seg, str):
            out += [int(ch) for ch in reversed(seg)]
        else:
            _, block, var = seg
            out.append(run(tuple(int(ch) for ch in reversed(block)), **{var: 1}))
    return out
def cfg(segs):
    return ('B', to_stream(segs) + [BLANK], [BLANK], '>')
TAILC = c + '1111' + c + '0' + a1 + '0' + '1'   # c 1^4 c 0 a1 0 1
ACC = accr(2) + [run(U3, b=1)]
ITEMS = {
 'T1': (KB(ACC, tok(1), []),
        cfg([c, a2, ('R', c * 12, 'b'), c * 4, '1', c, a1, '0', '1', c, '0', TAILC]), ()),
 'T2': (KB(ACC, tok(1), list(Z)),
        cfg([c, a2, ('R', c * 12, 'b'), c * 7, a1, TAILC]), ()),
 'T3': (KB(ACC, tok(1), [run(Z * 2, i=1)] + list(Z) * 2),
        cfg([a2, '1', c, '0', ('R', a1 + '0' * 1, 'x'), a1, '11', ('R', c + '00' + '1', 'i'), c, '0', TAILC]), ()),
 'T4': (KB(ACC, tok(1), [run(Z * 2, i=1)] + list(Z) * 3),
        cfg([c, a2, ('R', c * 12, 'b'), c * 7, a1, c, '1', ('R', c + '00' + '1', 'i'), c, '0', TAILC]), ()),
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
            traceback.print_exc(limit=2)
    text = header('cyc') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(sys.argv[1], 'w', newline='\n').write(text)
