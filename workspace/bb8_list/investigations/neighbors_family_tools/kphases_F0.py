"""Planner phase definitions for the F-shape K family (A0:0RF relatives of the parent):

    Kf(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 F> 0^inf      (kfam shape ('F', '0'))

    python kphases_F0.py TM [PHASE ...]      -> runs the planner (planner8.drive) on each phase, verbose

Phases (l, rr unknown; b, r symbolic), found for 0RF1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB1LF_0LH1LF_1RF---:
  ADD   : l 1 0 1^b 0 F> 0^inf             -> l 0 1^(b+3) 0 F> 0^inf          (R1: a -> a-1, b -> b+3)
  ENTRY : l 0 0 1^b 0 F> 0^inf             -> l 0 1^(b+3) C> 0^inf
  LOOP  : l 0 0 1^(r+3) C> 0 rr            -> l 0 1^(r+2) C> 0 1 0 rr        (as in the parent)
  FINAL1: l 1 0 1^(r+3) C> 0 (10)^i 0^inf  -> l 0 1^(r+1) 0 1 1 0 F> (10)^i 0^inf
          (with r+3 = 2 the machine halts: G0 H1; this is the k = b+1 boundary)
  SHIFT : l 0 1 1 0 F> (10)^n r            -> l (01)^n 0 1 1 0 F> r   (hand-written Coq lemma: the block
          "0 1 1 0" walks right through (10) pairs; the planner's fixed-context crossings cannot express it)
  FINAL = FINAL1 + SHIFT:  l 1 0 1^(r+3) C> 0 (10)^i 0^inf -> l 0 1^(r+1) (01)^i 0 1 1 0 F> 0^inf
  END4  : 0^inf 1 1 C> 0 (10)^i 0^inf      -> 0^inf 1 1 0 F> (10)^i 0^inf, then SHIFT: 0^inf (10)^i 1 1 0 F>
"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive

ONE = (1,)
Bv = {'b': 1}
R = {'r': 1}
I = {'i': 1}
T10 = mkrun((1, 0), I)


def phases():
    return {
        'ADD': (('F', [0] + mkrun(ONE, Bv) + [0, 1, V('l')], [BLANK], '>'),
                ('F', [0, 1, 1, 1] + mkrun(ONE, Bv) + [0, V('l')], [BLANK], '>')),
        'ENTRY': (('F', [0] + mkrun(ONE, Bv) + [0, 0, V('l')], [BLANK], '>'),
                  ('C', [1, 1, 1] + mkrun(ONE, Bv) + [0, V('l')], [BLANK], '>')),
        'LOOP': (('C', [1, 1, 1] + mkrun(ONE, R) + [0, 0, V('l')], [0, V('rr')], '>'),
                 ('C', [1, 1] + mkrun(ONE, R) + [0, V('l')], [0, 1, 0, V('rr')], '>')),
        'FINAL1': (('C', [1, 1, 1] + mkrun(ONE, R) + [0, 1, V('l')], [0] + T10 + [BLANK], '>'),
                   ('F', [0, 1, 1, 0] + mkrun(ONE, R) + [1, 0, V('l')], T10 + [BLANK], '>')),
        'END4': (('C', [1, 1, 0, BLANK], [0] + T10 + [BLANK], '>'),
                 ('F', [0, 1, 1, BLANK], T10 + [BLANK], '>')),
    }


COQ = {
    'ADD': 'forall b l, (0 >> [1]^^b *> 0 >> 1 >> l) {{F}}> const 0 -->+ '
           '(0 >> 1 >> 1 >> 1 >> [1]^^b *> 0 >> l) {{F}}> const 0',
    'ENTRY': 'forall b l, (0 >> [1]^^b *> 0 >> 0 >> l) {{F}}> const 0 -->+ '
             '(1 >> 1 >> 1 >> [1]^^b *> 0 >> l) {{C}}> const 0',
    'LOOP': 'forall r l rr, (1 >> 1 >> 1 >> [1]^^r *> 0 >> 0 >> l) {{C}}> 0 >> rr -->+ '
            '(1 >> 1 >> [1]^^r *> 0 >> l) {{C}}> 0 >> 1 >> 0 >> rr',
    'FINAL1': 'forall r i l, (1 >> 1 >> 1 >> [1]^^r *> 0 >> 1 >> l) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
              '(0 >> 1 >> 1 >> 0 >> [1]^^r *> 1 >> 0 >> l) {{F}}> [1;0]^^i *> const 0',
    'END4': 'forall i, (1 >> 1 >> 0 >> const 0) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
            '(0 >> 1 >> 1 >> const 0) {{F}}> [1;0]^^i *> const 0',
}

if __name__ == '__main__':
    tm = sys.argv[1]
    pl.set_tm(tm)
    ph = phases()
    for w in sys.argv[2:] or list(ph):
        s, t = ph[w]
        try:
            drive(w, s, t, matchers=(), maxev=300, verbose=True)
        except Exception as e:
            print('  ERROR', type(e).__name__, e)
