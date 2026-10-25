"""Cell strings at the H0 events of the r=2 branch (C7), for round analysis.  python h0fit.py t u P s y"""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
from c7sim import C7
from r2d0 import word
from brle import brle
def h0s(t, L, P, s, y, l='11'):
    sm = Sim(C7, word(t, L, P, s, y, l), state='B'); out = []
    while True:
        if sm.q == 'H' and sm.t[sm.pos] == 0:
            w, lo, r = sm.word(); out.append((w[lo:sm.pos], w[sm.pos:r + 1]))
        if not sm.step(): break
        if len(out) > 200: break
    return out
if __name__ == '__main__':
    t, u, P, s, y = map(int, sys.argv[1:6])
    for i, (a, b) in enumerate(h0s(t, 15 * u + 17, P, s, y)):
        print(i + 1, brle(a)[-140:], '<H>', brle(b)[:120])
