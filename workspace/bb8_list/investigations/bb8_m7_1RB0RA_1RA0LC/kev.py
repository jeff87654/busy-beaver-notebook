import sys, subprocess
from tokv import *
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
def parse(bits):
    if not bits.endswith('0111001'): return None
    R=bits[:-7]
    # R = prefix tokens + r-run : split trailing (10)^r
    j=len(R); r=0
    while j>=2 and R[j-2:j]=='10': j-=2; r+=1
    return R[:j], r
word,N,f,l = sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
out = subprocess.run(['./snap.exe',M,word,'B',N,str(f),str(l)],capture_output=True,text=True).stdout
prev=None
for line in out.splitlines():
    p=line.split()
    if len(p)==2 and p[0].isdigit():
        pr=parse(p[1])
        if pr is None: print(p[0],'NOTAIL', rl(tokview(p[1]))[:300]); prev=None; continue
        pre,r=pr
        tv=tokview(pre)
        key=tv[:-1]
        if key!=prev:
            print(p[0], rl(tv)[:400], 'r=%d'%r)
        prev=key
    else: print(line[:200])
