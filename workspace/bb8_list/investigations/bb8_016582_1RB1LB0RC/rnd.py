# random test: real orbit config, then replace "old" L bits with random bits (no-111 or arbitrary)
from canon import *
import random,sys
random.seed(int(sys.argv[1]))
mode=sys.argv[2]
L=[];P='01';G=[2]*3
# run real orbit some steps
N=random.randint(1000,200000)
for i in range(N): L,P,G=step(L,P,G)
# randomize L except last k bits
k=int(sys.argv[3])
n=len(L)
def rb(prev):
    while True:
        b=random.randint(0,1)
        if mode=='no111' and b==1 and prev[-2:]==[1,1]: continue
        return b
newL=[]
for i in range(n-k):
    newL.append(rb(newL))
L=newL+L[n-k:] if k>0 else newL
try:
    for i in range(200000): L,P,G=step(L,P,G)
    print('ok')
except Stuck as e: print('STUCK',e,i)
