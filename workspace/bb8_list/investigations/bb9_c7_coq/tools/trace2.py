"""Literal C7 trace from a D0f word: H0 events and B> moments in block-RLE.  python trace2.py t L P s y maxsteps [noB]"""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
from c7sim import C7
from trace import show
from r2d0 import word
t, L, P, s, y, maxs = map(int, sys.argv[1:7]); noB = len(sys.argv) > 7
sm = Sim(C7, word(t, L, P, s, y), state='B')
while sm.steps < maxs:
    if sm.q == 'H' and sm.t[sm.pos] == 0: print('H0 %d | %s' % (sm.steps, show(sm)))
    if not sm.step(): print('HALT', sm.steps, show(sm)); break
    if not noB and sm.q == 'B' and sm.t[sm.pos] == 0 and sm.t.rfind(1) == sm.pos - 1: print('B> %d | %s' % (sm.steps, show(sm)))
