import sys,re
from lit import *
TM="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
N=int(sys.argv[1]); which=sys.argv[2]
def bl(s):
    out=[]
    for i in range(0,len(s),2):
        b=s[i:i+2]
        if out and out[-1][0]==b: out[-1][1]+=1
        else: out.append([b,1])
    return ' '.join(b if n==1 else f'{b}^{n}' for b,n in out)
def cb(k,tape,pos,st):
    if 'ABCDEFGH'[st] in which:
        if not tape: return
        lo=min(tape); hi=max(tape)
        # align so pos is block start
        lo-= (pos-lo)%2 if False else 0
        L=''.join(str(tape.get(i,0)) for i in range(lo,pos))
        if len(L)%2: L='0'+L
        R=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
        if len(R)%2: R+='0'
        print(k,'ABCDEFGH'[st],bl(L)+' ['+'ABCDEFGH'[st]+'] '+bl(R))
r=run(TM,N,cb)
print(r[0],r[1])
