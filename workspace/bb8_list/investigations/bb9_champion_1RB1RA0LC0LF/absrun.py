import sys,time
sys.path.insert(0,'.')
from absm import tz
def run(maxiter, maxlist=2*10**6):
    ds=[]; a=1; b=2   # start: blank run gives K(;2;0)? use K(;1;3) known
    ds=[]; a=1; b=3
    it=0; ev=[]
    t0=time.time()
    while it<maxiter:
        it+=1
        if a>=1:
            n=a
            if not ds and a>=1:
                # R1 down to a=0 then R4 -- but only a==1 merge; general: b+=3a
                pass
            b+=3*a; a=0
            if not ds and a==0:
                ev.append(('R4',it,b))
                if b%2: ev.append(('HALT',b)); return ev,ds,a,b
                ds=[2,0]+[1,0]*(b//2); a=1; b=0
                if len(ds)>maxlist: ev.append(('listtoolong',len(ds))); return ev,ds,a,b
            continue
        k=tz(ds)
        if k==len(ds):
            ev.append(('R4',it,b)); 
            if b%2: ev.append(('HALT',b)); return ev,ds,a,b
            ds=[2,0]+[1,0]*(b//2); a=1; b=0; continue
        if k==0:
            ds[-1]-=1; a=b+2; b=1; continue
        if 2*k<=b:
            i=len(ds)-1-k
            ds[i]-=1
            ds=ds[:i+1]+[b+2-2*k]+[2]*(k-1)
            a=2; b=1; continue
        ev.append(('BIG',k,b,it)); return ev,ds,a,b
    return ev,ds,a,b
if __name__=='__main__':
    ev,ds,a,b=run(int(sys.argv[1]))
    print(ev[:20]); print(len(ds),a,b if b<10**50 else 'big')
