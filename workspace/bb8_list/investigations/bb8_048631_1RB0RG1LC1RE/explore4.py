import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
# LOOP round: L = 1 l ; H> 0 1 (01)^(r+2) 0^3 rr  ->  L = 1 0 0 1 l ; H> 0 1 (01)^(r+1) 0^2 rr
q = int(sys.argv[1]) if len(sys.argv) > 1 else 2
R = [0, 1] + mkrun(U, {'r': 1}, q) + [0, 0, 0, V('rr')]
T = [0, 1] + mkrun(U, {'r': 1}, q - 1) + [0, 0, V('rr')]
drive('LOOP', ('H', [1, V('l')], R, '>'), ('H', [1, 0, 0, 1, V('l')], T, '>'), matchers=(), maxev=60)
