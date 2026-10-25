from sim import *
import sys
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); S=sys.argv[4]; lo0=int(sys.argv[5])
prev=[None]
def cb(i,tape,pos,s):
    if a<=i<b and s in S:
        ones=[p for p,v in tape.items() if v]
        lm=min(ones) if ones else 0
        if pos<=lm+2:
            hi=max(tape)
            print('%7d'%i,''.join((('['+s+']') if p==pos else ' ')+str(tape.get(p,0)) for p in range(lo0,hi+2)))
run(N,cb)
