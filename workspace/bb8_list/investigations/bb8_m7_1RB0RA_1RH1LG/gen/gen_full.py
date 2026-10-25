"""All machine-level lemmas that were generated and compiled for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF."""
import sys, time
from common import *
from shapes import *
import mexp
from gen_all import ITEMS, KB, U3
import gen_rb
TODO = '''
(* ------------------------------------------------------------------------------------------------------------
   PARTIAL FILE (no nonhalt theorem; check.py does not PASS it).  Machine-level lemmas, all compiled:

   Families (tokens D(m) = (10)^m 1, accumulator (10)^r, tail S = 111001, head in B at the right end):
     K0 ds m r : with the left end "11" (P); the K(ds;a;b) of the champion, token 3d+1, r = 3b+2
     K1 ds m r : P-less (blank left of the leftmost token), tokens m >= 1 not = 0 mod 3, leftmost may be = 2 mod 3.
   R1  : K (m+3) r              -->+ K m (2r+4)                      (any context "1 :: l" left of the tokens)
   R2  : K (x+3 :: ds) 1 r      -->+ K (x :: ds) (2r+3) , r := 2     (context 1::l)   R2B: same, blank to the left
   R3  : K (1^(k+1) ++ x+3 :: ds) 1 r -->+ ... refill 2r+3, r := 2  (context 1::l)   R3B: same, blank to the left
   D2A : K1 [2;1] r -->+ K1 [2r+3] 2        D2B : K1 [2; 1^(k+2)] r -->+ K1 [2r+3; 1^(k+1)] 2   (blank to the left)
   REBUILD : K0 (1^(n+1)) 1 (3b+2) -->+ K1 ([6b+5] ++ 1^(n+2)) 2       (forall b n; P = 11 consumed)
 
   TODO (see the report bb8_m7_1RB0RA_1RH1LG.md):
     1. init_reach: c0 -->* K0 (2 :: 0^10) 0 0 in 2467 literal steps (step 2467, K(2,0^10;0;0)).
     2. used-up lists K1 (1^j) 1 r (all tokens 1, r = 3b+2): transient into the translated cycler
        L 0 1^N c 1^4 c 0 a1 0 1  -->+ (70 steps)  L 0 1^(N+2) c 1^4 c 0 a1 0 1  (cycle lemma, all N, L) and its proof
        of non-halting.  The transient depends on j (cases j = 1, 2, then j odd / even >= 3 with a loop over zero pairs).
        mexp.explore fails on the loops over b of the first phases (stuck at 0^inf 1 1 (10)^(6b) <C ...).
     3. abstract glue: step_fam for K0 / K1 (R1, R2/R3 incl. B variants, D2, REBUILD, used-up), progress_nonhalt_cond.
   ------------------------------------------------------------------------------------------------------------ *)
'''
if __name__ == '__main__':
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name, (s, t, pos) in ITEMS.items():
        tree = mexp.explore(s, t, positive=frozenset(pos))
        g = mexp.Gen(name)
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
        lemmas.extend(g.lemmas)
    tree = mexp.explore(gen_rb.START, gen_rb.TARGET)
    g = mexp.Gen('RB')
    rules.append(mexp.rule_lemma('REBUILD', gen_rb.START, gen_rb.TARGET, tree, g, progress=True))
    lemmas.extend(g.lemmas)
    text = header('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF (partial)') + '\n' + TODO + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(sys.argv[1], 'w', newline='\n').write(text)
    print('lemmas', len(lemmas), 'rules', len(rules))
