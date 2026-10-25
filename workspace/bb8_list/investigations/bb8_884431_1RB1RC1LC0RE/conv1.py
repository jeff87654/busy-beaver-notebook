import sys
from tmlit import Sim, ST
from fam import TM
def G(j,i,m): return '0' + '1'*(2*j) + '0111'*i + '0' + '1'*m
def nextA(word):
    s = Sim.from_word(TM, word, 0, 'A', size=1<<14)
    while s.steps < 100000:
        if not s.step(): return ('HALT', s.steps)
        if ST[s.state]=='A' and s.pos==s.lo and s.tape[s.pos]==0 and not any(s.tape[s.lo:s.pos]):
            return (s.steps, ''.join(map(str,s.tape[s.pos:s.hi+1])).rstrip('0'))
    return ('TIMEOUT',)
bad=0
for j in range(1,6):
  for i in range(0,4):
    for m in (8,9,12,16):
        r = nextA(G(j,i,m)); exp = G(j-1,i+1,m+ (1 if True else 0))
        print(j,i,m,r[0], r[1]==G(j-1,i+1,m), r[1] if r[1]!=G(j-1,i+1,m) else '')
print('----')
for j in range(2,9):
    rs = set()
    for i in range(0,5):
        for m in (8,9,12,16,20):
            r = nextA(G(j,i,m)); rs.add((r[0], r[1]==G(j-1,i+1,m)))
    print(j, rs)
