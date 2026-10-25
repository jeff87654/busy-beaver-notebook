import sys, os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate
TM = "1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---"
pl.set_tm(TM)
def PS(z, zc, c, cc, d, dc, left=None):
    L = [1] + mkrun((0,), z, zc) + ([V('l')] if left is None else left)
    R = mkrun((0,1,0,1), c, cc) + [0] + [0,1,0,1,0,1] + mkrun((1,0,1,0,1), d, dc) + [BLANK]
    return ('E', pl.norm_side(L), pl.norm_side(R), '>')
s = PS({'z':1}, 1, {'c':1}, 1, {'d':1}, 0)
t = PS({'z':1}, 0, {'c':1}, 0, {'d':1}, 1)
for vals in ({'z':2,'c':5,'d':0},{'z':1,'c':3,'d':2},{'z':3,'c':4,'d':1}):
    print(vals, validate.reaches(s,t,vals,max_steps=3000))
print('grid (rows c, cols d); entries steps or . ; for z in 0..2')
for z in (0,1,2):
    print('z =',z)
    for c in range(0,8):
        print(' c=%d'%c, ' '.join(('%5s'%(validate.reaches(s,t,{"z":z,"c":c,"d":d},max_steps=3000) or '.')) for d in range(0,6)))
