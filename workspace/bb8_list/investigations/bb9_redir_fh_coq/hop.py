import pickle
from common import *
from planner8 import is_run
S1 = pickle.load(open('st0a_stuck.pkl', 'rb'))
q, L, R, mode = S1
jpos = [k for k, t in enumerate(L) if is_run(t) and t[2] == (('J', 1),)][0]
JBLK = L[jpos][1]
FAR = L[jpos + 1:]
def XH(k='k', i='i'):
    Lx = tok(7) + [1, 1] + [run(JBLK, **{k: 1})] + FAR
    Rx = [1, run(Z, **{i: 1}), BLANK]
    return ('E', Lx, Rx, '>')
