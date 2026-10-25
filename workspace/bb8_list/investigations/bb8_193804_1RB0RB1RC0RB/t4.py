from sim import *
import sys
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); S=sys.argv[4]
lo0=int(sys.argv[5]) if len(sys.argv)>5 else -30
def cb(i,tape,pos,s):
    if a<=i<b and s in S:
        hi=max(tape)
        print('%7d'%i,''.join((('['+s+']') if p==pos else ' ')+str(tape.get(p,0)) for p in range(lo0,hi+2)))
run(N,cb)
