# rcheck.py: read tparse output on stdin; check consecutive tick moments against the P-token rule table.
import sys, re
def lt(s):
    nP=0; nJ=0; first=None
    for tok in s.split():
        m=re.match(r'(P|J[\d.]+)(?:\^(\d+))?$',tok); k=int(m.group(2) or 1)
        if m.group(1)=='P': nP+=k
        elif m.group(1)=='J1.0': nJ+=k
        if first is None: first=m.group(1)
    return nP,nJ,first
def predict(v):
    # returns (tokens, next vector) or None
    if v==[2,0,2,2]: return 2,[3,9,0,2],'init'
    if len(v)==4 and v[2]==0 and v[3]==2:
        u,r=v[0],v[1]
        return (1,[u+5,r-1,0,2],'pretick') if r>=1 else (2,[3,2,u+5,0],'preturn')
    if len(v)==4 and v[3]==0:
        u,r,B=v[0],v[1],v[2]
        if r>=1: return 1,[u+5,r-1,B,0],'tick'
        if B>=3: return 2,[3,u+7,B-2,0],'turn'
        if B==1: return 2,('CARRY',(u+3)//2),'carry'
    return None
prev=None; stats={}; bad=0
for line in sys.stdin:
    if '| R:' not in line: continue
    step=int(line.split()[0]); L=line.split('| L:')[1].split('| R:')[0]; R=line.split('| R:')[1].split()
    if R[-1]!='s1': continue
    v=[int(x) for x in R[:-1] if not x.startswith('!')]
    if L.strip()=='?': continue
    nP,nJ,first=lt(L)
    cur=(step,v,nP,nJ,first)
    if prev:
        ps,pv,pP,pJ,pf=prev
        pr=predict(pv)
        if pv[:2]==[1,0] and all(x==2 for x in pv[2:]):  # carry moment -> after transfer
            M=len(pv)-2; ok = (v==[2,0,2,2] and nP==pP+M-1+1 - 1 + 0) ; key='transfer'
            # expected: P^(M-1) pushed; check delta
            ok = (v==[2,0,2,2] and nP-pP==M and nJ in (pJ,pJ+2)); key="transfer" if nJ==pJ+2 else "transfer_r1"
        elif pr is None: key='norule'; ok=False
        else:
            k,nv,key=pr
            if key=='carry': ok = (v[:2]==[1,0] and len(v)-2==nv[1] and nP-pP==-1); 
            else: ok = (v==nv and pP-nP==k and nJ==pJ)
            if not ok and nJ==pJ-1 and pP-nP==k:
                key+='+Q'; q=list(nv) if isinstance(nv,list) else None
                if q and key.startswith(('tick','pretick')): q[0]+=1; ok=(v==q)
        stats.setdefault(key,[0,0]); stats[key][0 if ok else 1]+=1
        if not ok and (bad<15 or 'Q' not in key): 
            if bad<40: print('DEV',key,ps,pv[:8],'P',pP,'J',pJ,'->',step,v[:8],'P',nP,'J',nJ)
            bad+=1
    prev=cur
print('STATS',stats)
