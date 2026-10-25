import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RG_1LC1RE_1LD0LD_0RA1LC_0RF0LC_1LG1RH_1LB1RG_1RF---'
pl.set_tm(ACT)
U = (0, 1)
which = sys.argv[1]
if which == 'R2':
    R = [0, 1, 1, 1] + mkrun(U, {'b': 1}) + [0, 0, 0, 1] + mkrun(U, {'y': 1}) + [V('l')]
elif which == 'R2b':
    R = [0, 1, 1, 1] + mkrun(U, {'b': 1},1) + [0, 0, 0, 1] + mkrun(U, {'y': 1}) + [V('l')]
elif which == 'R3':  # b>=1, k zero digits
    R = [0, 1, 1, 1] + mkrun(U, {'b': 1}) + [0] + mkrun((0,), {'k': 1}) + [0, 0, 1] + mkrun(U, {'y': 1}) + [V('l')]
drive(which, ('A', [BLANK], R, '>'), None, matchers=(), maxev=int(sys.argv[2]) if len(sys.argv)>2 else 60)
