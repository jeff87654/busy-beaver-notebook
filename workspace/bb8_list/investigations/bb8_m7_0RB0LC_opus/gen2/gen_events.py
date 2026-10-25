"""Machine-level lemmas for the non-champion events of the second epoch (tail T1j):
   D2   : [x+5, 2, 1] r      -->+ [x] (4r+10)            tail j -> j+1
   R0a  : [x+4, 0, 1] r      -->+ [x, 2r+3, 1] 2
   R0b  : [x+4, 0, 1^(k+1), 1] r -->+ [x, 2r+3, 1^(k+1), 1] 2
   A2   : [x+3, 2] r         -->+ [x, 2r+2, 2, 1] 2
usage: python gen_events.py OUT.v [names...] [-v]"""
import sys, time
from common import *
import shapes
from shapes import *
import mexp
def tail_plus1():
    return [1, 0, 0, 1, 0, 0] + list(SIX) + [run(SIX, j=1)] + [1] * 8
def Kt(tail, acc, atok, rest):
    return ('B', tail + acc + atok + rest + [1, V('l')], [BLANK], '>')
ITEMS = [
    ('D2', lambda: (K(accr(0, 'r'), tok(1), tok(2) + tok(5, 'x')),
                    Kt(tail_plus1(), accr(10, 'r', (0, 1, 0, 1, 0, 1, 0, 1)), tok(0, 'x'), [])), ('r',)),
    ('R0a', lambda: (K(accr(0, 'r'), tok(1), tok(0) + tok(4, 'x')),
                     K(accr(2), tok(1), tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x'))), ('r',)),
    ('R0b', lambda: (K(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(0) + tok(4, 'x')),
                     K(accr(2), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x'))), ('r',)),
    ('A2', lambda: (K(accr(0, 'r'), tok(2), tok(3, 'x')),
                    K(accr(2), tok(1), tok(2) + tok(2, 'r', (0, 1, 0, 1)) + tok(0, 'x'))), ('r',)),
]
def W_D2():
    return ('B', [1, 0, 0, 1, 0, 0, run(SIX, j=1)] + list(SIX) + [1] * 9 + [0, 0] + [1, 0, 1, run((0, 1, 0, 1), r=1)] + tok(3, 'x') + [1, V('l')], [BLANK], '>')
ITEMS += [
    ('D2a', lambda: (K(accr(0, 'r'), tok(1), tok(2) + tok(5, 'x')), W_D2()), ('r',)),
    ('D2b', lambda: (W_D2(), Kt(tail_plus1(), accr(10, 'r', (0, 1, 0, 1, 0, 1, 0, 1)), tok(0, 'x'), [])), ()),
]
if __name__ == '__main__':
    out = sys.argv[1]; only = [a for a in sys.argv[2:] if not a.startswith('-')]
    shapes.TAIL = 'T1'
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name, mk, pos in ITEMS:
        if only and name not in only: continue
        s, t = mk()
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
        except Exception as e:
            print('%s: FAILED %r' % (name, str(e)[:600])); continue
        if '-v' in sys.argv: print('\n'.join(mexp.describe(tree)))
        g = mexp.Gen(name)
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0))
    text = header('second-epoch events (tail T1j)') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(out, 'w', newline='\n').write(text)
