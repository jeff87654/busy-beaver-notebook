"""Run planner8 on the rule phases of 1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH."""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
TM = "1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH"
pl.set_tm(TM)
I = {'i': 1}; K = {'k': 1}
R = [V('r')]
O2, O3, W = (1, 1), (1, 1, 1), (0, 1, 1)
def A_(right): return ('A', [BLANK], right, '>')
PHASES = [
  ('P1', A_([0, 1] + mkrun(O2, I) + [0, 1] + R), A_([0, 1] + mkrun(O2, I, 2) + [0] + R)),
  ('P2', A_([0, 1] + mkrun(O2, I) + [0, 0, 1, 0, 1, 1] + R), A_([0, 1, 0] + mkrun(O2, I, 2) + [1, 0, 1] + R)),
  ('P3', A_([0, 1] + mkrun(O2, I) + [0, 0, 1, BLANK]), A_([0, 1] + mkrun(O2, I, 4) + [BLANK])),
  ('P4', A_([0] + mkrun(O3, K, 1) + [BLANK]), A_([0, 1, 0, 1, 1, 1, 1, 1, 0, 1] + mkrun(W, K) + [BLANK])),
  ('P5', A_([0, 1] + mkrun(O3, K, 3) + [BLANK]), A_([0, 1] + mkrun(O2, {}, 8) + [0, 1, 1, 1, 0, 1] + mkrun(W, K) + [BLANK])),
  ('P6', A_([0, 1, 1] + mkrun(O3, K) + [BLANK]), ('C', [1, BLANK], [0] + mkrun(W, K, 1) + [BLANK], '>')),
]
if __name__ == '__main__':
    only = sys.argv[1:] 
    for name, start, target in PHASES:
        if only and name not in only: continue
        script, cfg = drive(name, start, target, maxev=400, verbose=True)
        print('   script:', script)
