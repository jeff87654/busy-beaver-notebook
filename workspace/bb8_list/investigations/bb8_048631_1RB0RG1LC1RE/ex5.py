import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RG_1LC1RE_1LD0LD_0RA1LC_0RF0LC_1LG1RH_1LB1RG_1RF---'
pl.set_tm(ACT)
U = (0, 1)
which=sys.argv[1]
if which=='FIN':
    R = mkrun(U, {'r': 1}, int(sys.argv[3])) + [0,0,1,0, V('w')]
    drive('FIN', ('A', [0,1,1,0,0,V('l')], R, '>'), None, matchers=(), maxev=int(sys.argv[2]))
elif which=='TRN':
    R = [0,1,1,1, V('w')]
    drive('TRN', ('A', [0,1,1,0,V('l')], R, '>'), ('A',[0,V('l')],[0,1,1,1,0,0,1,V('w')],'>'), matchers=(), maxev=int(sys.argv[2]))
