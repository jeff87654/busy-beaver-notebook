import sys,re
from lit import *
TM=sys.argv[3] if len(sys.argv)>3 else "1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
N=int(sys.argv[1]); which=sys.argv[2]
def rl(s):
    return ' '.join(f'{m.group(0)[0]}^{len(m.group(0))}' if len(m.group(0))>1 else m.group(0)[0] for m in re.finditer(r'0+|1+',s))
def cb(k,tape,pos,st):
    if 'ABCDEFGH'[st] in which:
        if not tape: print(k,'blank');return
        lo=min(tape); hi=max(tape)
        s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
        print(k,'ABCDEFGH'[st],pos-lo,len(s),rl(s[:pos-lo])+' ['+'ABCDEFGH'[st]+'] '+rl(s[pos-lo:]))
r=run(TM,N,cb)
print(r[0],r[1])
