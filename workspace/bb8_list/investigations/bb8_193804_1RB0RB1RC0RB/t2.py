from sim import *
import sys
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
def cb(i,tape,pos,s):
    if a<=i<b and s=='H': print(i,s,show(tape,pos,s))
run(N,cb)
