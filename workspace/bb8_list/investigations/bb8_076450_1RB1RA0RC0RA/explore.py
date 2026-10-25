"""Phase definitions for the planner (planner8.py) for
1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---"
pl.set_tm(TM)
ONE = (1,)
R1 = {'r': 1}; M = {'m': 1}; I = {'i': 1}
PH = {
 # TR1: 1 0 1 l B>0  ->  l 0 1111 A>0      (stream order, nearest first)
 'TR1': (('B', [1, 0, 1, V('l')], [BLANK], '>'),
         ('A', [1, 1, 1, 1, 0, V('l')], [BLANK], '>')),
 # TR2: 1^r 0 1 l A>0 -> 1^(r+4) 0 l A>0
 'TR2': (('A', mkrun(ONE, R1) + [0, 1, V('l')], [BLANK], '>'),
         ('A', [1, 1, 1, 1] + mkrun(ONE, R1) + [0, V('l')], [BLANK], '>')),
 # ENTRY: 1^m 0 0 l A>0 -> 1^(m+4) 0 l C>0
 'ENTRY': (('A', mkrun(ONE, M) + [0, 0, V('l')], [BLANK], '>'),
           ('C', [1, 1, 1, 1] + mkrun(ONE, M) + [0, V('l')], [BLANK], '>')),
 # LOOP: 1^(r+3) 0 0 l C> 0 rr -> 1^(r+2) 0 l C> 0 1 0 rr
 'LOOP': (('C', [1, 1, 1] + mkrun(ONE, R1) + [0, 0, V('l')], [0, V('rr')], '>'),
          ('C', [1, 1] + mkrun(ONE, R1) + [0, V('l')], [0, 1, 0, V('rr')], '>')),
 # FINAL: 1^(r+3) 0 1 l C> 0 (10)^i 0^inf -> (10)^(i+1) 1^(r+3) 0 l B> 0^inf
 'FINAL': (('C', [1, 1, 1] + mkrun(ONE, R1) + [0, 1, V('l')], [0] + mkrun((1, 0), I) + [BLANK], '>'),
           ('B', [1, 0] + mkrun((1, 0), I) + [1, 1, 1] + mkrun(ONE, R1) + [0, V('l')], [BLANK], '>')),
 # END4: 1 1 0 0 l C> 0 (10)^i 0^inf -> (10)^(i+1) 1 1 0 l B> 0^inf
 'END4': (('C', [1, 1, 0, 0, V('l')], [0] + mkrun((1, 0), I) + [BLANK], '>'),
          ('B', [1, 0] + mkrun((1, 0), I) + [1, 1, 0, V('l')], [BLANK], '>')),
}
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH]:
        s, t = PH[w]
        drive(w, s, t, matchers=(), maxev=300, verbose=True)
