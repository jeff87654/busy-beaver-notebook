from sim import *
import sys
N=int(sys.argv[1])
st={'lo':0,'hi':0}
def cb(i,tape,pos,s):
    if pos<st['lo']:
        st['lo']=pos; print(i,'L',s,show(tape,pos,s))
    if pos>st['hi']:
        st['hi']=pos; print(i,'R',s,show(tape,pos,s))
run(N,cb)
