import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RG_1LC1RE_1LD0LD_0RA1LC_0RF0LC_1LG1RH_1LB1RG_1RF---'
pl.set_tm(ACT)
U = (0, 1)
Lh = [0,1,1,0,V('l')]
c = int(sys.argv[3])
if sys.argv[2]=='S':
    R = mkrun(U, {'r': 1}, c) + [0,0,1,0,1] + mkrun(U,{'y':1}) + [V('rr')]
    T = [0,1,1,1] + mkrun(U, {'r': 1}, c-1) + [0,0,1] + mkrun(U,{'y':1}) + [V('rr')]
else:
    R = mkrun(U, {'r': 1}, c) + [0,0,1,0,V('rr')]
    T = [0,1,1,1] + mkrun(U, {'r': 1}, c-1) + [0,0,V('rr')]
drive('FIN', ('A', Lh, R, '>'), ('A',Lh,T,'>'), matchers=(), maxev=int(sys.argv[1]))
