from planner8 import *
B = lambda s: tuple(int(c) for c in s)
C = {'c': 1}; Bv = {'b': 1}
start = ('A', [BLANK], [0] + list(B('10100100')) + mkrun(B('10100100'), C) + list(B('10001001')) + mkrun(B('01001001'), Bv, 1) + [V('r')], '>')
target = ('A', [BLANK], [0] + list(B('10100100')) + mkrun(B('10100100'), C, 2) + list(B('10001001')) + mkrun(B('01001001'), Bv) + [V('r')], '>')
script, cfg = drive('S1 bounce (QS alignment)', start, target, maxev=60)
