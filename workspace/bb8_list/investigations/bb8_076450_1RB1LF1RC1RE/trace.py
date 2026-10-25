import sys
from lit import Sim, MAIN, compress, ST
# trace from 0^inf A>0 word 0^inf, print every step until next left-edge A0
w = sys.argv[1]; maxs = int(sys.argv[2]) if len(sys.argv) > 2 else 400
s = Sim(MAIN, size=4096)
base = s.pos
for i, c in enumerate(w):
    s.tape[base+1+i] = int(c)
s.hi = base + len(w)
print(s.steps, s.show(comp=False))
while True:
    st, sym = s.state, s.tape[s.pos]
    ok = s.step()
    print(s.steps, ST[st]+str(sym), s.show(comp=False))
    if not ok: break
    if s.state == 0 and s.tape[s.pos] == 0 and not any(s.tape[:s.pos]): break
    if s.steps > maxs: break
