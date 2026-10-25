import sys, re
sys.path.insert(0, '.')
from lit import Sim, ST, compress
M = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG"
if len(sys.argv) > 2: M = sys.argv[2]
s = Sim(M, size=1<<16)
N = int(sys.argv[1])
def parseX(R):
    # R = string to the right of head (head reading 0 in state E, left blank)
    m = re.match(r'^1((?:10)*)((?:01)*)(.*)$', R)
    a = len(m.group(1))//2; b = len(m.group(2))//2; r = m.group(3)
    return a, b, r
prev = None
while s.steps < N:
    if s.state == 4 and s.pos <= s.lo and s.tape[s.pos] == 0:
        t = s.tape; hi = s.hi
        while hi > s.pos and t[hi] == 0: hi -= 1
        R = ''.join(map(str, t[s.pos+1:hi+1]))
        a, b, r = parseX(R)
        if b == 0 or '-v' in sys.argv:
            print(s.steps, 'X(%d,%d, %s)' % (a, b, compress(r) if len(r) < 400 else compress(r[:200]) + '...' + str(len(r))))
    if not s.step():
        print("HALT", s.steps, s.show()); break
