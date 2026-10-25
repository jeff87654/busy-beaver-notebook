import sys,re
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
nL,nR=int(sys.argv[2]),int(sys.argv[3])
tm={}
for i,r in enumerate(M.split('_')):
    for c in range(2):
        t=r[3*c:3*c+3]
        tm[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
tape={}
def get(i): return tape.get(i,0)
import os
N0=int(os.environ.get('NG_START','0'))
p=0;q=0
W=os.environ.get('NG_TAPE')
if W:
    q=1
    for i,ch in enumerate(W): tape[i-len(W)]=int(ch)
for _ in range(N0):
    w,d,n=tm[(q,get(p))]; tape[p]=w; p+=d; q=n
def cfg():
    l=''.join(str(get(p-j)) for j in range(nL,0,-1))  # left window, farthest first
    r=''.join(str(get(p+j)) for j in range(1,nR+1))
    return f"{l} [{chr(65+q)}{get(p)}] {r}"
path=[ln.split(None,1)[1].strip() for ln in open(sys.argv[1]) if re.match(r'\s*\d+ [01]+ \[',ln)]
div=None
for i,c in enumerate(path):
    rc=cfg()
    if rc!=c:
        div=i;break
    t=tm[(q,get(p))]
    if t is None: print('real halts at',i);break
    w,d,n=t; tape[p]=w; p+=d; q=n
print('path length',len(path),'first divergence at',div)
if div is not None:
    print('abstract:',path[div-1]); print('real    :',cfg() if False else '')
    # recompute real previous cfg
    print('abstract prev:',path[div-1]); print('abstract now :',path[div]); print('real now     :',rc)
