# thr68.py: per rule type and depth j, A values (0..j+12, both parities) where the F68 engine rule fails literally
from lit68 import litnext
from f68eng import step,show
def cases(kind,j):
    if kind=='B': return [tuple([0]*j+[1,3,0]),tuple([0]*j+[2,0,1]),tuple([0]*j+[1]),tuple([0]*j+[4]),tuple([0]*j+[1,1,1])]
    if kind=='T': return [tuple([0]*(j+1))]
out=open('thr_out.txt','w')
for kind in 'BT':
    for j in list(range(1 if kind=='B' else 0,13))+[20]:
        bad=[];res={}
        for A in range(0,j+13):
            for L in cases(kind,j):
                st=(A,L,-1); pred,r=step(st); got=litnext(st)
                if got!=pred: bad.append(A); res[A]=(show(st),show(pred),got if not isinstance(got,tuple) else show(got))
        s='%s %d fail A: %s %s'%(kind,j,sorted(set(bad)),[res[a] for a in sorted(res)][:2])
        print(s,flush=True); out.write(s+'\n'); out.flush()
