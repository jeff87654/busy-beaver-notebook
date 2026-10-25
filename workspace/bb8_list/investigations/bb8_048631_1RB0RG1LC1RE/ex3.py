import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RG_1LC1RE_1LD0LD_0RA1LC_0RF0LC_1LG1RH_1LB1RG_1RF---'
pl.set_tm(ACT)
U = (0, 1)
# k=2 zero digits, S y with y symbolic, b = r+3
R = [0, 1, 1, 1] + mkrun(U, {'r': 1}, 4) + [0, 0, 0] + [0,0,1,0] + [V('l')]
drive('K', ('A', [BLANK], R, '>'), None, matchers=(), maxev=int(sys.argv[1]) if len(sys.argv)>1 else 60)
