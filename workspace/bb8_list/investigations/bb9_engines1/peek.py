"""peek.py MACHINE STARTFILE LABEL STEPS [EVERY]: literal run from a start line; prints token view with the head"""
import sys
from eng import *
m, sf, lab, N = sys.argv[1], sys.argv[2], sys.argv[3], int(float(sys.argv[4]))
ev = int(float(sys.argv[5])) if len(sys.argv) > 5 else N
for l in open(sf):
    f = l.split()
    if f[0] == lab: w, h, q = f[1], int(f[2]), f[3]
s = Sim.from_word(m, w, h, q, size=1 << 20)
nxt = ev
while s.steps < N:
    if not s.step():
        print('HALT', s.steps, s.last); break
    if s.steps >= nxt:
        nxt += ev
        word, lo = tape_word(s); hp = s.pos - lo
        print(s.steps, 'ABCDEFGHIJ'[s.state], '|', tokstr(tokens(word[:hp].lstrip('0'))), f'[{word[hp]}]', tokstr(tokens(word[hp+1:].rstrip('0'))))
