import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RG_1LC1RE_1LD0LD_0RA1LC_0RF0LC_1LG1RH_1LB1RG_1RF---'
pl.set_tm(ACT)
U = (0, 1)
R = [0,1,1,1] + mkrun(U, {'r': 1}, 1) + [0,0,0,0,V('w')]
T = mkrun(U, {'r': 1}, 2) + [0,0,0,V('w')]
drive('TR', ('A', [BLANK], R, '>'), ('A',[0,1,1,BLANK],T,'>'), matchers=(), maxev=30)
