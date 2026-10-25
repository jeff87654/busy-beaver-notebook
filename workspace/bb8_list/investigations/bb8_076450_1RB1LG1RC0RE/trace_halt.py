import sys
from nextA import from_word
from lit import Sim, MAIN, compress, ST
# trace the halting reset 1^n 00 for n = 8, printing every step
n = int(sys.argv[1]); tail = sys.argv[2] if len(sys.argv) > 2 else ''
s = Sim(MAIN, size=4096)
base = s.pos
w = '1'*n + tail
for i, c in enumerate(w):
    s.tape[base+1+i] = int(c)
s.hi = base + len(w)
print(s.steps, s.show(comp=False))
while True:
    st, sym = s.state, s.tape[s.pos]
    ok = s.step()
    print(s.steps, ST[st]+str(sym), s.show(comp=False))
    if not ok: break
    if s.steps > 400: break
