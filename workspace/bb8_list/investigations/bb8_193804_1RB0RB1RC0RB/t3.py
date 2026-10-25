from sim import *
import sys
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); S=sys.argv[4]
def cb(i,tape,pos,s):
    if a<=i<b and s in S:
        lo=min(tape);hi=max(tape)
        L=''.join(str(tape.get(p,0)) for p in range(lo,pos))
        R=''.join(str(tape.get(p,0)) for p in range(pos,hi+1))
        print(i,s,[len(x) for x in L.split('0')],'|',[len(x) for x in R.split('0')])
run(N,cb)
