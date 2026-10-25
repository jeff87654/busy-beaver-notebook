import sys
sys.path.insert(0,'../neighbors_family_tools')
from tmlit import Sim, ST
from fam import TM
s = Sim(TM)
n=0
last=None
while s.steps < int(sys.argv[1]):
    if ST[s.state]=='A' and not any(s.tape[s.lo:s.pos]):
        w=''.join(map(str,s.tape[s.pos:s.hi+1])).rstrip('0')
        print(s.steps, w[::-1] )
        n+=1
        if n>int(sys.argv[2]): break
    if not s.step(): print('halt'); break
