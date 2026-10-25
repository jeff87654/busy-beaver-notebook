import sys,re,os
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
tm={}
for i,r in enumerate(M.split('_')):
    for c in range(2):
        t=r[3*c:3*c+3]; tm[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
nL,nR=int(sys.argv[2]),int(sys.argv[3])
path=[]
for ln in open(sys.argv[1]):
    m=re.match(r'\s*\d+ ([01]+) \[([A-H])([01])\] ([01]+)\s*$',ln)
    if m: path.append((m.group(1),ord(m.group(2))-65,int(m.group(3)),m.group(4)))
phys={}   # position -> value (assigned)
p=0
W=os.environ.get('NG_TAPE')
if W:
    for i,ch in enumerate(W): phys[i-len(W)]=int(ch)
    # blank elsewhere is only assumed beyond the finite tape: mark far cells as blank lazily
conf=0; conflicts=[]
def check_cfg(idx,p):
    l,q,m,r=path[idx]
    cells=[]
    for j in range(nL): cells.append((p-nL+j, int(l[j])))        # l is farthest first
    for j in range(nR): cells.append((p+1+j, int(r[j])))
    cells.append((p,m))
    for pos,v in cells:
        if pos in phys and phys[pos]!=v: conflicts.append((idx,pos-p,phys[pos],v))
        elif pos not in phys: phys[pos]=v
for idx in range(len(path)):
    l,q,m,r=path[idx]
    if idx==0 and not W:
        pass
    check_cfg(idx,p)
    t=tm[(q,m)]
    if t is None: print('halting config reached at path index',idx,'with',len(conflicts),'conflicts'); break
    w,d,n=t; phys[p]=w; p+=d
    if idx+1<len(path) and path[idx+1][1]!=n: print('state mismatch!',idx)
print('conflicts:',len(conflicts))
for c in conflicts[:40]: print('  idx %d rel.pos %d: assigned %d but path window says %d'%c)
