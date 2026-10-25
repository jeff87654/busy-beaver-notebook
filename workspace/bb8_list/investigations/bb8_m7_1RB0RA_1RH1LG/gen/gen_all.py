"""Machine-level lemmas for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF (P-less rebuild family)."""
import sys, time, traceback
from common import *
from shapes import *
import mexp

def KB(acc, atok, rest):
    """head in B on the blank right of the word; blank immediately left of the leftmost token (P-less)."""
    return ('B', tailpart() + acc + atok + rest + [BLANK], [BLANK], '>')

U3 = (0, 1, 0, 1, 0, 1)
ITEMS = {
 'R1': (K(accr(0, 'r'), tok(3, 'm'), []), K(accr(4, 'r', (0, 1, 0, 1)), tok(0, 'm'), []), ('r',)),
 'R2': (K(accr(0, 'r'), tok(1), tok(3, 'x')), K(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x')), ('r',)),
 'R3': (K(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x')),
        K(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x')), ('r', 'x')),
 # leftmost borrowed token, blank to its left
 'R2B': (KB(accr(0, 'r'), tok(1), tok(3, 'x')), KB(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x')), ('r',)),
 'R3B': (KB(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x')),
         KB(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x')), ('r', 'x')),
 # D2 stage: [2, 1^(k+2)] -> [2r+3, 1^(k+1)]   and   [2,1] -> [2r+3]
 'D2A': (KB(accr(0, 'r'), tok(1), tok(2)), KB(accr(2), tok(3, 'r', (0, 1, 0, 1)), []), ('r',)),
 'D2B': (KB(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(2)),
         KB(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1))), ('r',)),
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
    text = header('rules') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(sys.argv[1], 'w', newline='\n').write(text)
