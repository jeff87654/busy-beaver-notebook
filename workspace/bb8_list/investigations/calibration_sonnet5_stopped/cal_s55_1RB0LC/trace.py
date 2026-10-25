import sys
from lit import Sim, MAIN, compress, ST
# trace from 0^inf G>0 word 0^inf, print every step until next left-edge G0
w = sys.argv[1]; maxs = int(sys.argv[2]) if len(sys.argv) > 2 else 400
comp = len(sys.argv) > 3
s = Sim(MAIN, size=4096)
s.state = ST.index('G')
base = s.pos
for i, c in enumerate(w):
    s.tape[base+1+i] = int(c)
s.hi = base + len(w)
print(s.steps, s.show(comp=comp))
while True:
    st, sym = s.state, s.tape[s.pos]
    ok = s.step()
    print(s.steps, ST[st]+str(sym), s.show(comp=comp))
    if not ok: print('HALT'); break
    if s.state == 6 and s.tape[s.pos] == 0 and not any(s.tape[:s.pos]): break
    if s.steps > maxs: break
