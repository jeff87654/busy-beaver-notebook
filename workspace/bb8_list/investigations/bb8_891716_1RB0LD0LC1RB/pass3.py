import sys, os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate, coqgen
TM = os.environ.get('TM',"1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
pl.set_tm(TM)
def PS(z, zc, c, cc, d, dc, left=None):
    L = [1] + mkrun((0,), z, zc) + ([V('l')] if left is None else left)
    R = mkrun((0,1,0,1), c, cc) + [0] + [0,1,0,1,0,1] + mkrun((1,0,1,0,1), d, dc) + [BLANK]
    return ('E', pl.norm_side(L), pl.norm_side(R), '>')
s = PS({'z':1}, 3, {'c':1}, 2, {'d':1}, 0)
t = PS({'z':1}, 2, {'c':1}, 1, {'d':1}, 1)
print(pl.show(s)); print(pl.show(t))
print(validate.reaches(s,t,{'z':1,'c':2,'d':1},max_steps=3000))
tree = engine.explore(s, t)
print('\n'.join(engine.describe(tree))[:3000])
