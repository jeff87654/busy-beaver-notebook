import sys
from lit import *
from tok import *
TM="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
N=int(sys.argv[1]); which=sys.argv[2]
out=[]
def cb(k,tape,pos,st):
    if 'ABCDEFGH'[st] in which:
        out.append((k,pos,st,dict(tape)))
r=run(TM,N,cb)
prev=None
for k,pos,st,tape in out:
    if st==4 and tape.get(pos-1,0)==0 and False: pass
    if not tape: print(k,"blank"); continue
    lo=min(tape); hi=max(tape)
    s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    print(k,'ABCDEFGH'[st],pos-lo,len(s))
    print(s if len(s)<300 else s[:100]+'...'+s[-200:])
