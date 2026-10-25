"""successive family configs from a token config: python tchain.py "toks" r j NCONF MAXSTEPS"""
import sys
from tm import *
from tprobe import word, tail
toks = [int(x) for x in sys.argv[1].split(',')]
r, j, n, mx = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
s = Sim(M11, word(toks, r, j))
t = tail(j)
print(0, toks, r)
k = 0
s.step()
while s.steps < mx and k < n:
    f = at_family(s, t)
    if f:
        print(s.steps, f[0], f[1]); k += 1
    if not s.step():
        print('HALT', s.steps, s.view()[:400]); break
