import sys, re; from sim import *
# config: 0^inf [E]0 100 (11)^a 00 ((11)^d 00)* 1 0^inf
pat=re.compile(r'^100((?:11)*)00((?:(?:11)*00)*)1$')
def parse_cfg(tape,h,s):
    if s!=4: return None
    ks=[k for k,v in tape.items() if v]
    if not ks or h!=min(ks)-1: return None
    hi=max(ks)
    st=''.join(str(tape.get(i,0)) for i in range(h+1,hi+1))
    m=pat.match(st)
    if not m: return None
    a=len(m.group(1))//2
    ds=[len(x)//2 for x in m.group(2).split('00')[:-1]]
    return a,ds
if __name__=='__main__':
    M = M1 if sys.argv[1]=='1' else M2
    T=parse(M); tape={}; h=0; s=0; step=0; N=int(sys.argv[2])
    while step<N:
        b=tape.get(h,0); t=T[(s,b)]
        if t is None: print('HALT',step); break
        tape[h]=t[0]; h+=t[1]; s=t[2]; step+=1
        if s==4:
            c=parse_cfg(tape,h,s)
            if c: 
                a,ds=c
                # compress ds
                print(step,'a=',a,'n=',len(ds),'ds=',ds[:4],'...',ds[-2:] if len(ds)>4 else '')
