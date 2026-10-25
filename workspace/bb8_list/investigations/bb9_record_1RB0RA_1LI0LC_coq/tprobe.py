"""token-level probe: python tprobe.py "4,21,4,20,1" a_tok r j"""
import sys
from tm import *
def tail(j): return '11' + '11111100' * j + '1001'
def nxt(w, t, mx=3*10**6):
    s = Sim(M11, w)
    s.step()
    while s.steps < mx:
        f = at_family(s, t)
        if f: return s.steps, f
        if not s.step(): return s.steps, ('HALT', s.view()[:300])
    return mx, None
def word(toks, r, j):
    return '11' + ''.join(D(m) for m in toks) + '10' * r + tail(j)
if __name__ == '__main__':
    toks = [int(x) for x in sys.argv[1].split(',')]
    r, j = int(sys.argv[2]), int(sys.argv[3])
    print(nxt(word(toks, r, j), tail(j)))
