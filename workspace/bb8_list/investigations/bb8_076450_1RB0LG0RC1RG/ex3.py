from planner8 import *
B = lambda s: tuple(int(c) for c in s)
J = {'j': 1}; K = {'k': 1}
def V1(jc, kc, r=[0, 1, 0, V('r')]):
    return ('G', [BLANK], list(B('0010')) + mkrun(B('01001010'), J, jc) + mkrun(B('01010010'), K, kc) + r, '>')
script, cfg = drive('bounce V1', V1(0, 1), V1(2, 0), maxev=80)
print(script)
