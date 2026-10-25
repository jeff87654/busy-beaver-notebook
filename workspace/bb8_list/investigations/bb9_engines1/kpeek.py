"""kpeek.py MACHINE STARTFILE LABEL STEPS Q SUF [MAXPRINT]: print every moment in state Q reading 0 whose left
neighbourhood is 1+SUF (K-moment shape), allowing junk on the right"""
import sys
from eng import *
m, sf, lab, N, Q, SUF = sys.argv[1], sys.argv[2], sys.argv[3], int(float(sys.argv[4])), sys.argv[5], sys.argv[6]
mp = int(sys.argv[7]) if len(sys.argv) > 7 else 40
for l in open(sf):
    f = l.split()
    if f[0] == lab: w, h, q = f[1], int(f[2]), f[3]
s = Sim.from_word(m, w, h, q, size=1 << 20)
qi = 'ABCDEFGHIJ'.index(Q); pat = [1] + [int(c) for c in SUF]; L = len(pat)
pr = 0
while s.steps < N and pr < mp:
    if not s.step():
        print('HALT', s.steps, s.last); break
    if s.state == qi and s.tape[s.pos] == 0 and list(s.tape[s.pos - L:s.pos]) == pat:
        word, lo = tape_word(s); hp = s.pos - lo
        print(s.steps, '|', tokstr(tokens(word[:hp - L + 1].lstrip('0'))), '+SUF [B0]', tokstr(tokens(word[hp+1:].rstrip('0')))[:150]); pr += 1
