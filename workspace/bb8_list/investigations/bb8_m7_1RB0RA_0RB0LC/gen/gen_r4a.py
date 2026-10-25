"""Machine-level lemma R4A: K0(n;b) = 11 (101)^(n+1) (10)^(3b+2) 111001 B>  -->+  M2 = (10)^(6b+4) 0 111 (001)^(n+3) B>  (explored by mexp)."""
import sys, time
from x1 import *
if __name__ == '__main__':
    pl.LEMMAS.clear()
    t0 = time.time()
    tree = mexp.explore(START, M2)
    g = mexp.Gen('R4A')
    rule = mexp.rule_lemma('R4A', START, M2, tree, g, progress=True, positive=())
    text = header('R4A start-up stage') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(g.lemmas) + '\n' + rule
    open(sys.argv[1], 'w', newline='\n').write(text)
    print('R4A: %d lemmas (%.1fs)' % (len(g.lemmas), time.time() - t0))
