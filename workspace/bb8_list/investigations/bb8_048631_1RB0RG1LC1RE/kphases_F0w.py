"""Planner phase definitions for the F-shape K family, WALK variant: the A0:0RF neighbors of
1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF--- that change D0 and keep F1 = 0RD, e.g.
0RF1RA_0RC0RA_0LD1RC_0LG1LE_1LF0LG_1LB0RD_0LH1LF_1RF---.

    Kf(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 F> 0^inf      (kfam shape ('F', '0'))

    python kphases_F0w.py TM KIND B3 [PHASE ...]   -> runs the planner (planner8.drive) on each phase, verbose

In these machines FINAL does not move a block through the (10) pairs (the A0 combination's SHIFT).  After the
refill, A0 walks right through the pairs and leaves them unchanged (hand-written Coq lemma WALK:
A> 0 1 0 1 0 -> 0 1 A> 0 1 0; the walker reads one cell of the next pair, which planner8's fixed-context
crossings cannot express), and a fixed tail FEND builds (a3, b3).  Two kinds (checked by gen_kcoq_F0.py
against the kfit fit):
  'A1' : R2 a = b + 2, b = b3;  R3 refill b + 2 - k, (a, b) = (1, b3);  R4 (1^(b+1)); 1; b3
         (D0 = 0LA: b3 = 0; D0 = 0LG: b3 = 1)
  'A0' : R2 a = b + 1, b = 3;   R3 refill b + 2 - k, (a, b) = (0, 3);   R4 (1^(b+1)); 0; 3   (D0 = 1LB, 1RC)
Phases (l, L unknown; b, r, i symbolic):
  ADD, ENTRY, LOOP : as in kphases_F0.py
  FIN1 : l 1 0 1^(r+3) C> 0 (10)^i 0^inf   -> l 0 1^(r+2) A> 0 1 0 (10)^i 0^inf
  E4A  : 0^inf 1 1 C> 0 (10)^i 0^inf       -> 0^inf 1 A> 0 1 0 (10)^i 0^inf
  WALK : L A> 0 1 0 (10)^n R               -> L (01)^n A> 0 1 0 R                 (hand-written)
  FEND : 'A1': L A> 0 1 0 0^inf            -> L 0 1^b3 0 F> 0^inf
         'A0': L 1 A> 0 1 0 0^inf          -> L 0 1 1 1 0 F> 0^inf
"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
from kphases_F0 import phases as phases_F0, COQ as COQ_F0

ONE = (1,)
R = {'r': 1}
I = {'i': 1}
T10 = mkrun((1, 0), I)
NAMES = ['ADD', 'ENTRY', 'LOOP', 'FIN1', 'E4A', 'FEND']


def phases(kind, b3):
    ph = {k: v for k, v in phases_F0().items() if k in ('ADD', 'ENTRY', 'LOOP')}
    ph['FIN1'] = (('C', [1, 1, 1] + mkrun(ONE, R) + [0, 1, V('l')], [0] + T10 + [BLANK], '>'),
                  ('A', [1] + mkrun(ONE, R) + [1, 0, V('l')], [0, 1, 0] + T10 + [BLANK], '>'))
    ph['E4A'] = (('C', [1, 1, 0, BLANK], [0] + T10 + [BLANK], '>'),
                 ('A', [1, BLANK], [0, 1, 0] + T10 + [BLANK], '>'))
    if kind == 'A1':
        ph['FEND'] = (('A', [V('L')], [0, 1, 0, BLANK], '>'),
                      ('F', [0] + [1] * b3 + [0, V('L')], [BLANK], '>'))
    elif kind == 'A0':
        ph['FEND'] = (('A', [1, V('L')], [0, 1, 0, BLANK], '>'),
                      ('F', [0, 1, 1, 1, 0, V('L')], [BLANK], '>'))
    else:
        raise ValueError(kind)
    return ph


def coq(kind, b3):
    c = {k: COQ_F0[k] for k in ('ADD', 'ENTRY', 'LOOP')}
    c['FIN1'] = ('forall r i l, (1 >> 1 >> 1 >> [1]^^r *> 0 >> 1 >> l) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                 '(1 >> [1]^^r *> 1 >> 0 >> l) {{A}}> 0 >> 1 >> 0 >> [1;0]^^i *> const 0')
    c['E4A'] = ('forall i, (1 >> 1 >> 0 >> const 0) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                '(1 >> const 0) {{A}}> 0 >> 1 >> 0 >> [1;0]^^i *> const 0')
    if kind == 'A1':
        c['FEND'] = ('forall L, L {{A}}> 0 >> 1 >> 0 >> const 0 -->+ (0 >> %s0 >> L) {{F}}> const 0'
                     % ''.join('1 >> ' for _ in range(b3)))
    else:
        c['FEND'] = ('forall L, (1 >> L) {{A}}> 0 >> 1 >> 0 >> const 0 -->+ '
                     '(0 >> 1 >> 1 >> 1 >> 0 >> L) {{F}}> const 0')
    return c


if __name__ == '__main__':
    tm = sys.argv[1]
    kind, b3 = sys.argv[2], int(sys.argv[3])
    pl.set_tm(tm)
    ph = phases(kind, b3)
    for w in sys.argv[4:] or NAMES:
        s, t = ph[w]
        try:
            drive(w, s, t, matchers=(), maxev=300, verbose=True)
        except Exception as e:
            print('  ERROR', type(e).__name__, e)
