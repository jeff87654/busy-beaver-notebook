import idle
import sys
def parse(M, mirror=True):
    tr={}
    for q,blk in enumerate(M.split('_')):
        for c in range(2):
            t=blk[3*c:3*c+3]
            if t[0]=='-': tr[(q,c)]=None
            else:
                d=1 if t[1]=='R' else -1
                if mirror: d=-d
                tr[(q,c)]=(int(t[0]),d,ord(t[2])-65)
    return tr
def word_to_K(s):
    # s = tape string from first 1 to last 1 ; template 101 (10)^d 00 ... (10)^a 00 (10)^(2b+1) 1
    return s
def run(M, steps, Q=1, maxev=50, start=None):
    tr=parse(M)
    T={} ; p=0; q=0
    lo=0; hi=-1
    ev=0
    for st in range(steps):
        c=T.get(p,0); t=tr[(q,c)]
        if t is None: print('HALT',st); return
        T[p]=t[0]
        if t[0]:
            lo=min(lo,p); hi=max(hi,p)
        p+=t[1]; q=t[2]
        if q==Q and T.get(p,0)==0 and p>hi:
            while hi>lo and not T.get(hi,0): hi-=1
            if p>hi:
                s=''.join(str(T.get(i,0)) for i in range(lo,hi+1)).lstrip('0')
                print(st+1, p-hi-1, s)
                ev+=1
                if ev>=maxev: return
if __name__=="__main__": M=sys.argv[1]; run(M,int(sys.argv[2]),maxev=int(sys.argv[3]))
