from absys import mstep
def rle(t):
    import itertools
    return ' '.join(k if len(list(g))==1 else k+'^%d'%len(list(itertools.groupby(t))) for k,g in itertools.groupby(t))
import itertools
def fmt(t):
    out=[]
    for k,g in itertools.groupby(t):
        n=len(list(g)); out.append(k if n==1 else '%s^%d'%(k,n))
    return ' '.join(out)
for i in range(1,9):
    for k in range(1,8):
        w='U'*i+'S'*k
        r=mstep(w,cap=2000000)
        print((i,k), r[0], fmt(r[1]) if r[0]!='HALT' and r[0]!='CAP' else '')
