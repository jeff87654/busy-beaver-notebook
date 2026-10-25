from psim import *
import sys
n=int(sys.argv[1]); mode=sys.argv[2]
if mode=='left':
    run(n, lambda q,s,pos,tape: pos==min(tape) if tape else True)
elif mode=='all':
    run(n, lambda q,s,pos,tape: True)
