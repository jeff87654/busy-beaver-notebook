import sys
from lit import Sim, MAIN, ST
word = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
s = Sim(MAIN, size=4096)
base = s.pos
for i, c in enumerate(word):
    s.tape[base + 1 + i] = int(c)
s.hi = base + len(word)
lo = base - 3
for _ in range(N):
    t = ''.join(str(x) for x in s.tape[lo:s.pos]) + '[' + ST[s.state] + str(s.tape[s.pos]) + ']' + ''.join(str(x) for x in s.tape[s.pos+1:base+len(word)+4])
    print(s.steps, t)
    if not s.step(): print('HALT'); break
    if s.state == 0 and s.tape[s.pos] == 0 and not any(s.tape[:s.pos]) and s.steps > 1: 
        print(s.steps, 'A0 left edge:', ''.join(str(x) for x in s.tape[lo:base+len(word)+4])); break
