# Exact run-length TM simulator with self-loop sweeps (literal semantics, accelerated).
from sim import parse, M1, M2
class RSim:
    def __init__(self, M, left, head, right, state):
        # left: list of [bit,count] nearest-last ; right: list of [bit,count] nearest-last
        self.T=parse(M); self.L=[list(x) for x in left]; self.R=[list(x) for x in right]
        self.h=head; self.s=state; self.steps=0; self.halted=False
    @staticmethod
    def push(st,b,n):
        if n<=0: return
        if not st and b==0: return
        if st and st[-1][0]==b: st[-1][1]+=n
        else: st.append([b,n])
    @staticmethod
    def pop(st):
        if not st: return 0
        b=st[-1][0]; st[-1][1]-=1
        if st[-1][1]==0: st.pop()
        return b
    def step(self):
        t=self.T[(self.s,self.h)]
        if t is None: self.halted=True; return False
        w,d,ns=t
        if ns==self.s:
            # sweep: current cell plus the whole run of same symbol in direction d
            src=self.R if d==1 else self.L; dst=self.L if d==1 else self.R
            n=1
            if src and src[-1][0]==self.h:
                n+=src[-1][1]; src.pop()
            self.push(dst,w,n); self.h=self.pop(src); self.steps+=n
            return True
        if d==1: self.push(self.L,w,1); self.h=self.pop(self.R)
        else: self.push(self.R,w,1); self.h=self.pop(self.L)
        self.s=ns; self.steps+=1; return True
    def run_until(self, pred, maxsteps):
        while self.steps<maxsteps:
            if not self.step(): return 'HALT'
            if pred(self): return 'HIT'
        return 'TIMEOUT'
    def ones(self):
        return sum(c for b,c in self.L+self.R if b==1)+self.h

def kconfig(M,a,ds):
    # 0^inf [E]0 100 (11)^a 00 ((11)^d 00)* 1 0^inf
    right=[[1,1]]
    for d in reversed(ds):
        RSim.push(right,0,2); RSim.push(right,1,2*d)
    RSim.push(right,0,2); RSim.push(right,1,2*a); RSim.push(right,0,2); RSim.push(right,1,1)
    return RSim(M,[],0,right,4)
def parse_k(r):
    # state E, head 0, left all zero (empty), right = 1 00 (11)^a 00 ...
    if r.s!=4 or r.h!=0 or r.L: return None
    R=r.R[::-1]  # left to right
    if len(R)<3 or R[0]!=[1,1] : return None
    i=1
    if R[i][0]!=0: return None
    z=R[i][1]
    # prefix 1 00 then (11)^a then 00
    if z<2: return None
    if z>2:
        a=0; R2=[[0,z-2]]+R[i+1:]
    else:
        if R[i+1][0]!=1 or R[i+1][1]%2: return None
        a=R[i+1][1]//2; R2=R[i+2:]
    # R2 begins with 0^(2+2*k...) runs; parse digit list: alternating 0-runs (even) and 1-runs
    if not R2 or R2[-1]!=[1,1]: return None
    body=R2[:-1]; ds=[]
    # body = 0^2 (11)^d1 0^2 ... (11)^dn 0^2 -> zeros runs of length 2*(1+#empty digits)
    j=0
    if not body or body[0][0]!=0: return None
    while j<len(body):
        b,c=body[j]
        if b==0:
            if c%2: return None
            z=c//2  # number of separators
            ds.extend([0]*(z-1))  # z-1 zero digits between
            j+=1
            if j<len(body):
                b2,c2=body[j]
                if c2%2: return None
                ds.append(c2//2); j+=1
            else:
                break
        else: return None
    return a,ds
