from common import *
def Y(Tc=0, Tv='T', ac=0, zc=0, far=None):
    L = [0, 1] + tok(Tc, Tv) + tok(8) + tok(9) + (far if far is not None else [V('l')])
    R = list(Z) + [1] + [1, 0] * ac + [run((1, 0), a=1)] + [0] + list(Z) * zc + [run(Z, z=1), BLANK]
    return ('I', L, R, '>')
Y_START = Y(Tc=1, ac=2)
Y_TARGET = Y(Tc=0, zc=2)
