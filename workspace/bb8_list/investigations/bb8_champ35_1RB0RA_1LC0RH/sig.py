import sys
sys.path.insert(0,'.')
from tr import start
from tmlit import Sim
def sigma(ds,a,b,N=10**8):
    s=start(ds,a,b)
    while s.steps<N:
        if not s.step():
            return s.steps, s.ones()
    return None
if __name__=='__main__':
    for n in (1,2,3):
        row=[]
        for b in range(0,6):
            r=sigma([0]*n,0,b)
            row.append(r)
        print(n,row)
