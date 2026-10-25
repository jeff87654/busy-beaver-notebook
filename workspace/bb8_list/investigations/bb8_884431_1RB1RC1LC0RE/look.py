import sys
sys.path.insert(0,'../neighbors_family_tools')
from tmlit import Sim, ST
from fam import TM
s = Sim(TM)
n=0
while s.steps < int(sys.argv[1]):
    if ST[s.state]=='A':
        lo,hi=s.bounds()
        print(s.steps, s.show()[:200])
        n+=1
        if n>int(sys.argv[2]): break
    s.step()
