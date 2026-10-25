import pickle
from common import *
UNIT = (1, 1, 0, 0, 1)
E2 = pickle.load(open('st2e_end.pkl', 'rb'))
q, L, R, mode = E2
assert L[0] == ('run', UNIT * 3, (('u', 1),))
FAR = L[1:]
def X3(v='v', i='i'):
    """[far] (unit^3)^v D(2+3i) C> 0 D1^(2+3i) 100 [E2 right]"""
    Lx = [1] + [0, 1] * 2 + [run((0, 1) * 3, **{i: 1})] + [run(UNIT * 3, **{v: 1})] + FAR
    Rx = [0] + list(Z) * 2 + [run(Z * 3, **{i: 1})] + [1, 0, 0] + R
    return ('C', Lx, Rx, '>')
