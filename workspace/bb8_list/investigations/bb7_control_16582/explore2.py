from symsim import *
import sys
c=make_config('[A0]')
n=0
lim=int(sys.argv[1])
while n<lim:
    c.step(); c.normalize(); n+=1
    if not c.left: print(n, c.steps, c)
