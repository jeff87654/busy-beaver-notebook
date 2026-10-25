import idle, sys, collections, subprocess, os
from ana import load, kind
from fam import BASES
HERE=os.path.dirname(os.path.abspath(__file__))
def spn(m,O,Q,tapes,N):
    p=subprocess.Popen([os.path.join(HERE,'spn.exe'),m,O,Q,str(N)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'pids.txt'),'a') as f: f.write('%d spn.exe\n'%p.pid)
    o,_=p.communicate('\n'.join(tapes)+'\n'); return o.split('\n')
if __name__=='__main__':
    mode=sys.argv[1]; N=int(sys.argv[2])
    for nm in sys.argv[3:] or BASES:
        f=BASES[nm][3]; labs,V=load(nm,mode); O,Q=BASES[nm][1:3]
        tapes=[l.split()[0] for l in open('bat/%s.rare'%nm)]
        c=collections.Counter(); ex={}
        for m,outs in V:
            ks=''.join(kind(o,f) for o in outs)
            if 'T' not in ks: continue
            idx=[i for i,k in enumerate(ks) if k=="T"][:3]
            res=spn(m,O,Q,[tapes[i] for i in idx],N)
            res4=spn(m,O,Q,[tapes[i] for i in idx],4*N)
            for i,r,r4 in zip(idx,res,res4):
                t=r.split(); t4=r4.split()
                if t[0]=='H' or t4[0]=='H': k='H-late'
                else:
                    w=int(t[2])-int(t[1]); w4=int(t4[2])-int(t4[1]); o1=int(t[3]); o4=int(t4[3])
                    if w4==w and o4==o1: k='stuck'
                    elif w4>=3.5*w: k='linear'
                    else: k='sublinear(%.1f)'%(w4/w)
                    r=r+' / '+r4
                c[k]+=1; ex.setdefault(k,[]).append((m,labs[i][0],r))
        print(nm,mode,dict(c),flush=True)
        for k in ex:
            if k!='bounded':
                for e in ex[k][:3]: print('   ',k,e)
