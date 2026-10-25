import idle, sys, re
# check consecutive literal a=0 moments from blank against abstract maps
def expand(tokens):
    out=[]
    for t in tokens:
        if 'x' in t: v,n=t.split('x'); out+= [int(v)]*int(n)
        else: out.append(int(t))
    return out
if __name__!='__main__': fam=None
else: fam=sys.argv[1]
lines=[] if fam is None else [l for l in open(sys.argv[2]).read().split('\n') if ' : ' in l or ' | ' in l]
ok=bad=0
if fam=='C':
    import absC
    if len(sys.argv)>3: absC.NEWTOP=int(sys.argv[3])
    sts=[]
    for l in lines:
        r=expand(l.split('|')[-1].split())
        sts.append((r[:-2],r[-1]))
    for (R,y),(R2,y2) in zip(sts,sts[1:]):
        a=absC.astep(R,y)
        if a[0]==R2 and a[1]==y2: ok+=1
        else: bad+=1; print('BAD',R[:20],y,'->',a, 'lit',R2[:20],y2)
elif fam=='B':
    import absB
    sts=[]
    for l in lines:
        s=l.split(' : ')[1]
        c=None
        if '|' in s: c,s=s.split('|'); c=int(c)
        r=expand(s.split()); sts.append((c,r[:-2],r[-1]))
    for x,x2 in zip(sts,sts[1:]):
        a=absB.astep(*x)
        if tuple(a)==x2: ok+=1
        else: bad+=1; print('BAD',x,'->',a,'lit',x2)
elif fam=='A':
    import absA
    for l,l2 in zip(lines,lines[1:]):
        s=l.split(' : ')[1]; s2=l2.split(' : ')[1]
        toks=s.replace('|',' | ').split(); runs=[];seps=[];pend=' '
        for t in toks:
            if t=='|': pend='|'; continue
            for v in expand([t]):
                if runs: seps.append(pend)
                runs.append(v); pend=' '
        a=absA.astep(runs,seps)
        e=absA.fmt(*absA.canon(*a)) if a[0] is not None else str(a)
        if e==s2.strip(): ok+=1
        else: bad+=1; print('BAD',s,'->',e,'lit',s2)
if fam: print(fam,'ok',ok,'bad',bad)
