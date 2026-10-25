import sys,os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
from probe2 import *
from kfam import kword
def tapestr(s):
    lo=s.lo;hi=s.hi
    while lo<s.pos and s.tape[lo]==0: lo+=1
    return ''.join(str(x) for x in s.tape[lo:s.pos])+'['+ST[s.state]+']'+''.join(str(x) for x in s.tape[s.pos:hi+1])
from tmlit import ST
ds=tuple(int(x) for x in sys.argv[1].split(',')) if sys.argv[1] else ()
a=int(sys.argv[2]);b=int(sys.argv[3])
print(kword(ds,a,b))
s=kstart(TM,ds,a,b)
while True:
    s.step()
    r=parse_at(s)
    if r:
        print(s.steps,r); print(tapestr(s)); break
