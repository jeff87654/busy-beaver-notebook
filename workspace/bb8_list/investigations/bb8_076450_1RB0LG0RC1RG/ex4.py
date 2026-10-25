import sys
from planner8 import *
B = lambda s: tuple(int(c) for c in s)
abb = B('10100100'); bab = B('10010100')
N = {'n': 1}; J = {'j': 1}; M = {'m': 1}
def V1(jc, jl, kc, kl, r):
    return ('G', [BLANK], list(B('0010')) + mkrun(B('01001010'), jl, jc) + mkrun(B('01010010'), kl, kc) + [0, 1, 0] + r, '>')
def P(nc, nl, mc, ml, r=None):
    return ('A', [BLANK], [0] + mkrun(abb, nl, nc) + mkrun(bab, ml, mc) + [1, BLANK], '>')
def Q(nc, nl, mc, ml):
    return ('A', [BLANK], [0] + mkrun(abb, nl, nc) + [1, 0, 0] + mkrun(bab, ml, mc) + [1, BLANK], '>')
which = sys.argv[1]
r = [V('r')]
if which == 'E':
    drive('E', ('A', [BLANK], [0] + mkrun(abb, N) + [1, 0, 0, 1] + r, '>'), V1(0, {}, 0, N, r))
if which == 'E1':
    drive('E1', ('A', [BLANK], [0] + mkrun(abb, N, 1) + [1, 0, 0, 1] + r, '>'), V1(0, {}, 1, N, r))
if which == 'XP':
    drive('XP', V1(0, J, 0, {}, [0, 1, 0, 0] + r), ('A', [BLANK], [0] + mkrun(abb, J, 1) + [1, 0, 0] + r, '>'))
if which == 'XQ':
    drive('XQ', V1(0, J, 0, {}, [0, 0, 1, 0, 1, 0, 0] + r), ('A', [BLANK], [0] + mkrun(abb, J, 2) + r, '>'))
if which == 'XQ0':
    drive('XQ0', V1(0, J, 0, {}, [BLANK]), Q(2, {}, 1, J))
if which == 'ZP':
    drive('ZP', P(0, N, 0, {}), Q(2, {}, 0, N))
