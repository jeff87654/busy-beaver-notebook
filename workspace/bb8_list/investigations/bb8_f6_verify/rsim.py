"""rsim.py: exact rule-level simulator of F6's Round-1 tick automaton (rules validated literally, see REPORT).
State: RSA vector v (right side, sentinel omitted) + left token stream (list of [tok,count], head side = END of list).
Tokens: 'P' (1100, +5) or 'Q' (fat token from a carry, +6). Stops when the stream is empty (fuel exhausted -> prefix) or on an
unvalidated situation. Bulk-applies tick runs over P blocks."""
import sys
def pop(st, k=1):
    out=[]
    while k>0:
        if not st: return None
        t,c=st[-1]; take=min(c,k); out.append((t,take)); k-=take
        if take==c: st.pop()
        else: st[-1][1]=c-take
    return out
def push(st,t,c):
    if c<=0: return
    if st and st[-1][0]==t: st[-1][1]+=c
    else: st.append([t,c])
def run(v, st, maxcarries=10, log=print, maxev=10**6):
    consumed=0; carries=[]
    for ev in range(maxev):
        if not st: return ('FUEL_END', v, consumed, carries)
        if v==[2,0,2,2]:
            g=pop(st,2)
            if g is None or any(t!='P' for t,_ in g): return ('UNVALIDATED init with', g, v)
            v=[3,9,0,2]; consumed+=2; continue
        u,r,a,b=v
        if r>=1:  # tick run (pretick or stage tick): bulk over the top run of tokens
            t,c=st[-1]; k=min(c,r); pop(st,k); v=[u+(5 if t=='P' else 6)*k, r-k, a, b]; consumed+=k; continue
        if a==0 and b==2:   # preturn
            g=pop(st,2)
            if g is None or any(t!='P' for t,_ in g): return ('UNVALIDATED preturn with', g, v)
            v=[3,2,u+5,0]; consumed+=2; continue
        if b==0 and a>=3:   # turnaround
            g=pop(st,2)
            if g is None or any(t!='P' for t,_ in g): return ('UNVALIDATED turn with', g, v)
            v=[3,u+7,a-2,0]; consumed+=2; continue
        if b==0 and a==1:   # carry
            if u%2==0: return ('EVEN_U_CARRY (2^M tail branch, not modelled)', u, consumed)
            # need >=2 P tokens on top (validated with plenty)
            if st[-1][0]!='P' or st[-1][1]<3: return ('UNVALIDATED carry with', st[-3:], v)
            M=(u+3)//2; pop(st,2); push(st,'Q',2); push(st,'P',M-1)   # stream P^J -> P^(M-1) Q Q P^(J-2)
            carries.append((consumed, u, M)); log('carry #%d after %d tokens: U=%d (U mod 2=%d) M=%d, top of stream now %s' % (len(carries), consumed, u, u%2, M, st[-4:][::-1]))
            consumed+=1; v=[2,0,2,2]
            if len(carries)>=maxcarries: return ('MAXCARRIES', v, consumed, carries)
            continue
        return ('NO_RULE', v)
    return ('MAXEV', v)
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='round1':   # X(n,N): after transfer_r1 -> INIT with P^N
        N=int(eval(sys.argv[2])); res=run([2,0,2,2], [['P',N]], maxcarries=int(sys.argv[3]) if len(sys.argv)>3 else 10)
        print(res[0], res[1] if len(res)>1 else '', 'consumed=%s'%(res[2] if len(res)>2 else ''))
    if mode=='mid':      # S(J; u,r,B)
        J,u,r,B=map(int,sys.argv[2:6]); res=run([u,r,B,0], [['P',J]]); print(res[0], res[1] if len(res)>1 else '')
