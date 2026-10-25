"""Complete busycoq proof for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF (never halts).

  python gen_final.py OUT.v

Machine-level lemmas are explored and proved by mexp.py (copied from ../../bb8_m7_1RB0RA_1RH1LG/gen/, with an optional
MEXP_TRACE progress print): the champion rules R1, R2, R3 (context 1::l, gen_rules.py), the lifecycle rules STAGE, ENDA,
ENDB (gen_life.py), and the rebuild of a used-up list for n = 3 and n = 11 (wp.py waypoints, each leg checked literally
with `python wp.py check N`):  UAn: used list -> Z(6c+10, 1);  ZRn: Z(x+1, k) -> Z(x, k+2);  UBn: Z(0, 21+m) -> C1;
C12: C1 -> C2;  C23: C2 after six R1 steps -> C3.  The families, wrappers, invariants and the theorem are glue.v.in."""
import sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import *
from shapes import *
import mexp
import gen_rules, gen_life, wp

DOC = '''
(* ------------------------------------------------------------------------------------------------------------
   The machine runs the BB(7) champion's digit-list recursion on K-form tapes
     K ds a r = 0^inf 11 D(ds..) D(a) (10)^r 111001 B>      (tokens D(m) = (10)^m 1, ds nearest-first),
   all tokens = 1 mod 3 and r = 2 mod 3 (the champion's digits d <-> tokens 3d+1, r = 3b+2):
     R1   : a = m+3                      -> a = m, r -> 2r+4
     R2/R3: a = 1, nearest token t != 1  -> t -> t-3, the token right of it -> 2r+3, r := 2.
   Where the champion halts (E0 on the used-up list: all tokens 1, a = 1) this machine REBUILDS the list
   (n = 3 or 11 tokens left of the a-token, r = 3c+5; T = 3n+13):
     UAn  : used-up list           -->+ Z(6c+10, 1)        Z(x, k) = B on the blank left end of 0 (01)^x 00 (101)^k (100)^(n+2) 101
     ZRn  : Z(x+1, k)              -->+ Z(x, k+2)           (iterated by ZIT: Z(x, k) -->* Z(0, 2x+k))
     UBn  : Z(0, 21+m)             -->+ [T+3, 1^(11+m), 2, 0, 3 | 3]  r = 2                (C1)
     C12  : C1                     -->+ [T, 21, 1^(9+m), 0, 0 | 19]  r = 2                  (C2)
     R1 x6, then C23               -->+ [T, 21, 1^(7+m), 0, 1 | 762] r = 2                  (C3)
   and the rebuilt list runs a lifecycle with R1 chains on the a-token (a = 0 mod 3):
     STAGE: [T, 21, 1^(k+2), 0, 1 | 0] r -->+ [T, 21, 1^k, 0, 1 | 2r+2] 2
     ENDA : [T, 21, 1, 0, 1 | 0] r       -->+ [T, 20, 1 | 2r+2] 2
     ENDB : [T, 20, 1 | 0] r             -->+ [T, 16, 2r+3 | 1] 2        (a standard 3-token list)
   The 1-run has odd length 12c+7, so the stages end at k = 1.  The champion recursion keeps the token count, so the
   next used-up list has n = 3 again: n = 11 -> 3 -> 3 -> ... forever (the closed family below).
   ------------------------------------------------------------------------------------------------------------ *)
'''

def pieces():
    out = [(n, s, t, pos) for n, s, t, pos in gen_rules.ITEMS]
    out += [(n, s, t, pos) for n, (s, t, pos) in gen_life.ITEMS.items()]
    for n in (3, 11):
        out += [('UA%d' % n, wp.used(n), wp.W1(n), ()),
                ('ZR%d' % n, wp.ZS(n), wp.ZT(n), ()),
                ('UB%d' % n, wp.Z0(n), wp.C1(n), ())]
    out += [('C12', wp.C1g(), wp.C2g(), ()), ('C23', wp.C2r(), wp.C3r(), ())]
    return out

if __name__ == '__main__':
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name, s, t, pos in pieces():
        t0 = time.time()
        tree = mexp.explore(s, t, positive=frozenset(pos))
        g = mexp.Gen(name)
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), file=sys.stderr, flush=True)
    glue = (HERE / 'glue.v.in').read_text()
    used = (HERE / 'used.v.in').read_text() if (HERE / 'used.v.in').exists() else '(* USED: TODO *)'
    glue = glue.replace('@USED@', used)
    text = header('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF never halts') + '\n' + DOC + '\n' \
        + '(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
        + '\n(** ** Stage and loop lemmas (generated) *)\n\n' + '\n'.join(lemmas) \
        + '\n(** ** Machine-level rules (generated) *)\n\n' + '\n'.join(rules) + '\n' + glue
    Path(sys.argv[1]).write_text(text, newline='\n')
    print('wrote', sys.argv[1], len(lemmas), 'lemmas', len(rules), 'rules', file=sys.stderr)
