"""Exact independent block simulator for the seven-state L1 investigation.

Counts and times are Python integers. Only repeated identical block crossings
with identical entry and exit control are accelerated. Undefined A1 stops
before a halt action; reported time counts defined transitions only.
"""
from functools import lru_cache
from pathlib import Path
import json, re, sys

MACHINE = '1RB---_1RC1RD_0LD1LC_1RF0LE_0LG1LC_0RB0RG_0RA1LD'
TABLE = [[None if row[i:i+3]=='---' else
          (int(row[i]), 1 if row[i+1]=='R' else -1, ord(row[i+2])-65)
          for i in (0,3)] for row in MACHINE.split('_')]

class Sim:
    def __init__(self, k=12, word='', q=0, head=0):
        self.k=k; self.q=q; self.side=0; self.cur=0
        self.L=[]; self.R=[]; self.steps=0; self.macros=0; self.halted=False
        self.pos=0
        if word:
            pad=(-head)%k
            word='0'*pad+word
            head+=pad
            word+='0'*((-len(word))%k)
            blocks=[int(word[i:i+k],2) for i in range(0,len(word),k)]
            ix=head//k
            self.cur=blocks[ix]
            for b in blocks[:ix]: self.push(self.L,b)
            for b in reversed(blocks[ix+1:]): self.push(self.R,b)

    @staticmethod
    def push(stack,b,n=1):
        if not n or (not stack and b==0): return
        if stack and stack[-1][0]==b: stack[-1][1]+=n
        else: stack.append([b,n])

    @staticmethod
    def pop(stack):
        if not stack: return 0
        b=stack[-1][0]; stack[-1][1]-=1
        if not stack[-1][1]: stack.pop()
        return b

    @lru_cache(maxsize=None)
    def crossing(self,q,side,b):
        p=self.k-1 if side else 0
        seen=set(); steps=0
        while 0<=p<self.k:
            key=(q,p,b)
            if key in seen: raise RuntimeError('in-block cycle')
            seen.add(key)
            bit=1<<(self.k-1-p); read=int(bool(b&bit)); tr=TABLE[q][read]
            if tr is None: return q,p,b,steps,True
            w,d,q=tr
            b=(b|bit) if w else (b&~bit)
            p+=d; steps+=1
        return q,p,b,steps,False

    def step(self):
        q,p,b,t,halt=self.crossing(self.q,self.side,self.cur)
        self.macros+=1
        if halt:
            self.q=q; self.cur=b; self.steps+=t; self.halted=True; self.haltpos=p
            return
        right=p>=self.k; side=0 if right else 1
        ahead=self.R if right else self.L; behind=self.L if right else self.R
        n=1
        if q==self.q and side==self.side and ahead and ahead[-1][0]==self.cur:
            n+=ahead.pop()[1]
        self.push(behind,b,n)
        self.steps+=t*n; self.pos+=(self.k*n if right else -self.k*n)
        self.cur=self.pop(ahead); self.q=q; self.side=side

    def snapshot(self):
        return {'q':chr(65+self.q),'side':self.side,'cur':self.cur,
                'left':self.L,'right':self.R,'steps':self.steps,'macros':self.macros,'k':self.k}

    def word(self,limit=1000000):
        blocks=self.L+[[self.cur,1]]+list(reversed(self.R))
        n=sum(c for _,c in blocks)*self.k
        if n>limit: return None
        return ''.join(format(b,f'0{self.k}b')*c for b,c in blocks)

    def summary(self):
        def fmt(s): return ' '.join(f'{b:0{self.k}b}^{n}' for b,n in s)
        return f'{self.steps} {chr(65+self.q)} {self.side} | '+fmt(self.L)+f' [{self.cur:0{self.k}b}] '+fmt(reversed(self.R))

def compact(s):
    out=[]; i=0
    while i<len(s):
        best=(1,1)
        for p in (1,2,3,4,6,12):
            if i+p>len(s): continue
            pat=s[i:i+p]; j=i+p
            while s.startswith(pat,j): j+=p
            n=(j-i)//p
            if n>=3 and n*p>best[0]*best[1]: best=p,n
        p,n=best
        out.append(s[i:i+p] if n==1 else f'({s[i:i+p]})^{n}')
        i+=p*n
    return ''.join(out)

if __name__=='__main__':
    sim=Sim(int(sys.argv[1]) if len(sys.argv)>1 else 12)
    maxm=int(sys.argv[2]) if len(sys.argv)>2 else 100000
    out=Path(__file__).with_name('blank_trace.txt').open('w')
    count=0
    for _ in range(maxm):
        if not sim.L and sim.cur==0 and sim.q==6:
            count+=1
            if count<=40 or count%100==0:
                print(sim.summary(),file=out)
        sim.step()
        if sim.halted: break
    print(sim.summary(),file=out)
    out.close()
    Path(__file__).with_name('blank_snapshot.json').write_text(json.dumps(sim.snapshot()))
    print('macros',sim.macros,'steps',sim.steps,'halted',sim.halted,'events',count)
