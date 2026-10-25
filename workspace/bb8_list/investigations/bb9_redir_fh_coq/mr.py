import pickle
from common import *
S = pickle.load(open('st0b_end.pkl', 'rb'))
q, L, R, mode = S
B60 = L[0][1]
FARNEAR = L[1:-1 - 76]
D9 = tok(9)
assert tuple(L[-1 - 76:-1]) == tuple(D9 * 4), 'D9 stack'
def MR(w='w', l=V('l'), d9=0, rz=0):
    return (q, [run(B60, **{w: 1})] + FARNEAR + D9 * d9 + [l], R[:-2] + list(Z) * rz + [run(Z, i=1), BLANK], mode)
