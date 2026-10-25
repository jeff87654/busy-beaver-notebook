import sys
sys.path.insert(0, '.')
import kfam
from kfam import *
ORIG = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
def mirror(tm):
    return tm.replace('L','X').replace('R','L').replace('X','R')
MIR = mirror(ORIG)
set_shape('A','10')
