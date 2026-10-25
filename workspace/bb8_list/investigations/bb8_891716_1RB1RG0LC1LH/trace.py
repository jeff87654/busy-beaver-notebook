import sys
from sim import T, ST
# trace from a K configuration word (ds,a,b)
from kstep import kword
ds = eval(sys.argv[1]); a = int(sys.argv[2]); b = int(sys.argv[3]); N = int(sys.argv[4])
w = kword(ds, a, b)
off = 3
tape = [0]*off + [int(c) for c in w] + [0]*60
pos = off + len(w); st = 2
last = None
for s in range(N):
    e = T[st][tape[pos]]
    line = ''.join(map(str, tape[:pos])) + '[' + ST[st] + ']' + ''.join(map(str, tape[pos:pos+1])) + ''.join(map(str, tape[pos+1:pos+12])).rstrip('0')
    print('%3d %s' % (s, line))
    if e is None: print('HALT'); break
    tape[pos] = e[0]; pos += e[1]; st = e[2]
    if pos < 3: break
