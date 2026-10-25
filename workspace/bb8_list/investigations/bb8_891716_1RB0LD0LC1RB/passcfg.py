"""The pass lemma (waypoint found from concrete traces): see the report. Left stream: 1 0^(z+3) l ; right: (0101)^(c+2) 0 010101 (10101)^d."""
import sys, os
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V

def PS(z, zc, c, cc, d, dc):
    L = [1] + mkrun((0,), z, zc) + [V('l')]
    R = mkrun((0, 1, 0, 1), c, cc) + [0] + [0, 1, 0, 1, 0, 1] + mkrun((1, 0, 1, 0, 1), d, dc) + [BLANK]
    return ('E', pl.norm_side(L), pl.norm_side(R), '>')

def pass_rule():
    return (PS({'z': 1}, 3, {'c': 1}, 2, {'d': 1}, 0), PS({'z': 1}, 2, {'c': 1}, 1, {'d': 1}, 1))
