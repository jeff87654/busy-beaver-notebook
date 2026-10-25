import sys
from rulecheck import *
n=int(sys.argv[1]); b=int(sys.argv[2])
s = sim_from([0]*n, 0, b)
def disp(s):
    lo, hi = s.bounds()
    t = s.tape
    w = ''.join(map(str, t[lo:hi+1]))
    return '%s @%d %s' % (ST[s.state], s.pos-lo, w)
last = None
cnt=0
while True:
    if s.pos == s.lo and not any(s.tape[s.lo:s.pos]) :
        print(s.steps, disp(s)); cnt+=1
    if not s.step(): break
    if s.steps > 5000 or cnt>60: break
