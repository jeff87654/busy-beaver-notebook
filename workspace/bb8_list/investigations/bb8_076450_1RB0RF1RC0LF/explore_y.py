from rules_plan import *
import pext
for c, pre in ((0, [1, 1]), (1, [1])):
    R = [0] + run((0, 1, 0, 1, 0, 1), 'k') + [0, 1] * (6 + c) + [P.BLANK]
    cfg = ('A', [P.BLANK], R, '>')
    A0 = 4 + c  # A = 2k + 4 + c
    Lt = [0, 1, 0, 1, 0, 1, 1, 1, 0] + [0, 1, 0] * A0 + run((0, 1, 0, 0, 1, 0), 'k') + pre + [P.BLANK]
    tgt = ('B', Lt, [P.BLANK], '>')
    try:
        s, e = P.drive('Y3k+%d' % c, cfg, tgt, matchers=[m_tloop, pext.m_sweep], maxev=60)
        print(s)
    except Exception as ex:
        print('EXC', ex)
