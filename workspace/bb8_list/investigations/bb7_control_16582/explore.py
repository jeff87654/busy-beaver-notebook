from symsim import *
import sys
c=make_config('[A0]')
n=0; out=[]
lim=int(sys.argv[1]); lo=int(sys.argv[2]); hi=int(sys.argv[3])
while n<lim:
    c.step(); c.normalize(); n+=1
    if lo<=n<=hi: print(n, c.steps, c)
