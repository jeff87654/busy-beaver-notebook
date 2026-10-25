import idle, sys, collections
from ana import load, kind
from fam import BASES
FIX=['']
def runs(bits):
    if FIX[0]=='S-': bits=bits+'0'
    return [len(x) for x in bits[:-1].split('0')]
def forms(nm,mode):
    from fam import VAR
    FIX[0]=VAR.get(nm,'')
    labs,V=load(nm,mode); f='C'
    tapes=[l.split()[0] for l in open('bat/%s.rare'%nm)]
    base=[]
    for l in open('out/%s.m%s'%(nm,mode)):
        if l.startswith('#R '): base.append(l.split()[2])
    res=collections.Counter(); ex={}
    for m,outs in V:
        ks=''.join(kind(o,f) for o in outs)
        if set(ks)-{'='}!={'M'}: continue
        sig=set(); bad=False
        for i,o in enumerate(outs):
            if o=='=': continue
            lab=labs[i][0]
            if base[i][0]!='M': bad=True; break
            b=runs(base[i][1:]); v=runs(o[1:])
            # base: [top, 2^j, 3, refill..., 0, y]  find j (run of 2s after first element)
            j=1
            while j<len(b) and b[j]==2: j+=1
            tail=b[j:]          # 3, refill, 0, y
            nj=j-1
            # variant: P + 2^(nj+d) + tail
            if v[-len(tail):]!=tail: bad=True; sig.add('TAILDIFF:'+lab); break
            head=v[:-len(tail)]
            k=len(head)
            while k>0 and head[k-1]==2: k-=1
            P=tuple(head[:k]); d=len(head)-k-nj
            # parity-only matters for P's role; but record exact
            sig.add((lab.split()[0]+('t1' if 't=1' in lab else ('t' if 't=' in lab else '')),P,d))
        if bad: res['NONSTD']+=1; ex.setdefault('NONSTD',[]).append((m,sorted(map(str,sig))[:3])); continue
        # consistency per event type
        bytype=collections.defaultdict(set)
        for t,P,d in sig: bytype[t].add((P,d))
        if all(len(s)==1 for s in bytype.values()):
            key='STD '+' '.join('%s:P=%s,d=%+d'%(t,list(list(s)[0][0]),list(s)[0][1]) for t,s in sorted(bytype.items()))
        else:
            key='INCONSISTENT'; ex.setdefault(key,[]).append((m,dict((t,sorted(s)) for t,s in bytype.items())))
        res[key]+=1
    return res,ex
if __name__=='__main__':
    mode=sys.argv[1]
    for nm in sys.argv[2:]:
        res,ex=forms(nm,mode)
        print('==',nm,mode)
        for k,v in res.most_common(): print('  %4d %s'%(v,k))
        for k in ex:
            for e in ex[k][:3]: print('     ',k,e)
