import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
TM='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'
def kword(ds,a,b):
    w='1'
    for d in ds: w+='01'*(3*d+1)+'1'
    w+='01'*(3*a+1)+'1'+'01'*(3*b+1)+'10101'
    return w
def start(ds,a,b):
    w=kword(ds,a,b)
    return Sim.from_word(TM,'0000'+w+'0',4+len(w),'G')
if __name__=='__main__':
    ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); n=int(sys.argv[4])
    s=start(ds,a,b)
    print(s.show())
    prev=None
    for i in range(n):
        if not s.step(): print('HALT',s.steps,s.last); break
        if s.steps%int(sys.argv[5])==0: print(s.steps,s.show())
