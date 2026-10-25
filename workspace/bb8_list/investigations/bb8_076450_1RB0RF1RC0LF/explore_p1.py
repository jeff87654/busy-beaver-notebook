from rules_plan import *
import pext
X = [1, 1, 1, 0, 1, 1, 1, 0]
L = [0, 1, 0, 1, 0, 1, 1] + run((1, 1, 1), 'k') + [1, 1] + X + [0, 1, 0] * 5 + [P.V('l')]
cfg = ('B', L, [P.BLANK], '>')
Lt = [0, 1, 0, 1, 0] + [1] * 47 + run((1, 1), {'k': 3}) + X + [P.V('l')]
tgt = ('B', Lt, [P.BLANK], '>')
s, e = P.drive('P1', cfg, tgt, matchers=[m_tloop, pext.m_sweep], maxev=200)
print(s)
print(P.show(e))
