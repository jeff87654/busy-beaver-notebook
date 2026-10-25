import sys
from sim import T, ST
# trace from an explicit tape string (L->R) with head position and state
tape = [0]*4 + [int(c) for c in sys.argv[1]] + [0]*40
pos = 4 + int(sys.argv[2]); st = ST.index(sys.argv[3]); N = int(sys.argv[4])
for s in range(N):
    e = T[st][tape[pos]]
    line = ''.join(map(str, tape[:pos])) + '[' + ST[st] + ']' + ''.join(map(str, tape[pos:pos+1])) + ''.join(map(str, tape[pos+1:pos+14])).rstrip('0')
    print('%3d %s' % (s, line.lstrip('0')))
    if e is None: print('HALT'); break
    tape[pos] = e[0]; pos += e[1]; st = e[2]
