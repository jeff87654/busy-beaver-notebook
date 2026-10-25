"""Complete busycoq proof for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF (never halts).

  python gen_final.py OUT.v

Machine-level lemmas are explored and proved by mexp.py (gen/): the champion rules R1, R2, R3 (context 1::l),
R3B, D2B (leftmost token, blank to its left), REBUILD (gen/gen_rb.py), CYCLE (gen/gen_cyc1.py) and the used-up
transient U1, U2, U3, ZR, ZF, U4 (opus/ms3.py, waypoints checked with reach.exe / reachL.exe).
The families, the wrappers, the iteration ZIT, the invariants and the theorem are the template glue.v.in + init.v.in."""
import sys, time
from pathlib import Path
OPUS = Path(__file__).resolve().parent
sys.path.insert(0, str(OPUS.parent / "gen"))
from common import *
from shapes import *
import mexp
from gen_all import ITEMS as RULES
import gen_rb
from ms3 import M0, Y0, M2, ZB, ZS, ZT, Z02, M3k1, M4k1

DOC = '''
(* ------------------------------------------------------------------------------------------------------------
   The machine runs the BB(7) champion's digit-list recursion; where the champion halts (E0, the exhausted list)
   it rebuilds a longer list and keeps going, and when that list is used up it becomes a translated cycler.

   Families (tokens D(m) = (10)^m 1, accumulator (10)^r, tail 111001, head in B on the blank right of the word):
     K P11 ds a r      : level 0, the champion's family 0^inf 11 D(ds..) D(a) (10)^r 111001 B>  (11 tokens + a-token)
     K (const 0) ds a r : level 1, no "11" left of the leftmost token (13 tokens, leftmost = 2 mod 3, or 12 tokens)
   Rules (ds nearest-first, a = the a-token):
     R1  : a = m+3                 -> a = m, r -> 2r+4
     R2/R3 : a = 1, nearest token t != 1 (t = x+3): t -> x, the token right of it -> 2r+3, r := 2
     R3B : the same with t the leftmost token (blank to its left)     D2B : leftmost token 2 deleted, refill 2r+3
     REBUILD : level 0, all tokens 1, r = 3b+2  -->+  level 1 [6b+5, 1^12; a = 1; r = 2]
     used-up : level 1, 13 tokens 1, r = 3b+2  -->+  the translated cycler  L 0 1^N 110 1111 110 0 10 0 1 B>
               (U1, U2, U3 explored; ZR is one round of the bounce  Z(x+1,k) -> Z(x,k+2)  and ZIT iterates it).
   Invariants: tokens = 1 mod 3 except the leftmost at level 1 (= 2 mod 3 until D2B deletes it), r = 2 mod 3.
   ------------------------------------------------------------------------------------------------------------ *)
'''

CYC_START = ('B', [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1] + [run((1,), N=1)] + [0, V('l')], [BLANK], '>')
CYC_TARGET = ('B', [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1] + [run((1,), N=1)] + [1, 1] + [0, V('l')], [BLANK], '>')

PIECES = [(n, RULES[n][0], RULES[n][1], RULES[n][2], {}) for n in ('R1', 'R2', 'R3', 'R3B', 'D2B')] + [
    ('REBUILD', gen_rb.START, gen_rb.TARGET, (), {'prefix': 'RB'}),
    ('CYCLE', CYC_START, CYC_TARGET, (), {'prefix': 'CY', 'splits': 2}),
    ('U1', M0, Y0, (), {}),
    ('U2', Y0, M2, (), {}),
    ('U3', M2, ZB, (), {}),
    ('ZR', ZS, ZT, (), {}),
    ('ZF', Z02, M3k1, (), {}),
    ('U4', M3k1, M4k1, (), {}),
]

if __name__ == '__main__':
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name, s, t, pos, opt in PIECES:
        t0 = time.time()
        kw = {'positive': frozenset(pos)}
        if 'splits' in opt:
            kw['splits'] = opt['splits']
        tree = mexp.explore(s, t, **kw)
        g = mexp.Gen(opt.get('prefix', name))
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), file=sys.stderr)
    glue = (OPUS / "glue.v.in").read_text() + (OPUS / "init.v.in").read_text()
    text = header('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF never halts') + '\n' + DOC + '\n' \
        + '(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
        + '\n(** ** Stage and loop lemmas (generated) *)\n\n' + '\n'.join(lemmas) \
        + '\n(** ** Machine-level rules (generated) *)\n\n' + '\n'.join(rules) + '\n' + glue
    Path(sys.argv[1]).write_text(text, newline='\n')
    print('wrote', sys.argv[1], len(lemmas), 'lemmas', len(rules), 'rules', file=sys.stderr)
