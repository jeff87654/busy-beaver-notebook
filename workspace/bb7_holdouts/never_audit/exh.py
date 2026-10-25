import subprocess,sys,collections,os
from vcode import *
LIT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'src','lit.exe'))
def ktrace(m,steps,q=None,side=None):
    out=subprocess.run([LIT,'ends',m,str(steps),'*','*','100000000'],capture_output=True,text=True).stdout.splitlines()
    ev=[l.split(' ',3) for l in out if l[0].isdigit()]
    if q is None:
        c=collections.Counter((e[1],e[2]) for e in ev); (q,side),_=c.most_common(1)[0]
    res=[]
    for e in ev:
        if e[1]!=q or e[2]!=side: continue
        cells,h,_=lit_rle_to_cells(e[3])
        if side=='L': cells=cells[::-1]
        res.append((int(e[0]),vlist(cells),cells))
    return q,side,res,out[-1]
if __name__=='__main__':
    m=sys.argv[1]; steps=int(sys.argv[2]) if len(sys.argv)>2 else 3000000
    q,side,res,last=ktrace(m,steps)
    print(m,q,side,len(res),last[:20])
    prev=None
    for st,v,c in res:
        nz=sum(1 for x in v if x>0)
        if nz<=3 and st>50: print(st,v[:12],len(v))
