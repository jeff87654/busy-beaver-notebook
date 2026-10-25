"""Exhaustion #2 (parametric): Kt(0,0,1^n;1;3R2+2;3) -->+ cascade config.
  n = 3125*nn + 1792 (real class mod 5^5); R2 = Rp + 1 (Rp free) so parked 1^(12R2-10) = 1^(12*Rp+2).
  Far tokens (far->near): y1=1875nn+1077, D4, y2=1125nn+645, D6, y3=675nn+385, D6, A=y4=405nn+232;
  then parked 1^(12Rp+2), markers 0,2,z2, X=243nn+136, near list 1^(243nn+129); a=1,b=2,t=18."""
import sys, time
from common import *
from shapes import *
import mexp
def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')
def tv(c, coef):                      # D(coef*nn + c) nearest-first stream
    return [1] + [0, 1] * c + [run((0, 1) * coef, nn=1)]
# START: t=3, acc=(10)^(3R2+2) with R2=Rp+1 -> (01)^(5+3Rp); list 1^n = (101)^1792 ++ run((101)^3125, nn)
START = KK(3, accr(5, 'Rp', (0, 1) * 3), tok(1), list(Z) * 1792 + [run(Z * 3125, nn=1)])
# TARGET mid near-first: near list 1^(243nn+129), X, z2, D2, D0, parked 1^(12Rp+2), A=y4, D6, y3, D6, y2, D4, y1
mid = (list(Z) * 128 + [run(Z * 243, nn=1)]          # near list 1^(243nn+128)
       + tv(136, 243)                                 # X
       + [0, 0]                                        # z2
       + tok(2) + tok(0)                               # D2 D0  (the "2,0" before z2 in far->near: 0,2,z2)
       + list(Z) * 2 + [run(Z * 12, Rp=1)]            # parked 1^(12Rp+2)
       + tv(232, 405)                                  # A = y4
       + tok(6) + tv(385, 675)                         # D6 y3
       + tok(6) + tv(645, 1125)                        # D6 y2
       + tok(4) + tv(1077, 1875))                      # D4 y1
TARGET = KK(18, accr(2), tok(1), mid)
def probe():
    cfg = START; t0 = time.time()
    for k in range(600):
        ops, cfg, how = mexp.run_stuck(cfg, TARGET, budget=5000000)
        if how == 'target': print('TARGET in', k + 1, 'stages %.0fs' % (time.time() - t0)); return
        if how != 'stuck': print('stage', k, how, pl.show(cfg)[:120]); return
        lp = mexp.find_loop(cfg, 2)
        if lp is None: print('no loop stage', k, pl.show(cfg)[:140]); return
        cfg = lp.after()
    print('maxstages')
if __name__ == '__main__':
    if 'probe' in sys.argv: probe()
    else:
        pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
        tree = mexp.explore(START, TARGET, splits=0, maxstages=600)
        g = mexp.Gen('EXH2'); rule = mexp.rule_lemma('EXH2', START, TARGET, tree, g, progress=True)
        text = '(** C04 exhaustion #2 *)\n\nFrom BB8 Require Import Individual92.\nFrom Coq Require Import Lia PeanoNat List.\nImport ListNotations.\nSet Default Goal Selector "!".\nFrom Dev Require Import Base.\n\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(g.lemmas) + '\n' + rule
        open(sys.argv[1], 'w', newline='\n').write(text); print('wrote', sys.argv[1], len(g.lemmas), 'lemmas')
