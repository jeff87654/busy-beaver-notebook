# literal check of the F-turn rewrite rules R1-R4 with random contexts
import random
from sim import T
def run_to_F(tape, p):
    q='F'; first=True; lo=hi=p; steps=0
    while True:
        s=tape.get(p,0); t=T[(q,s)]
        if t is None: return None
        w,d,nq=t; tape[p]=w; p+=1 if d=='R' else -1; q=nq; steps+=1
        lo=min(lo,p); hi=max(hi,p)
        if q=='F': return p,lo,hi,steps
def check(before, fpos_before, after, fpos_after, trials=30):
    for _ in range(trials):
        tape={}
        for i in range(-20,0): tape[i]=random.randint(0,1)
        for i,c in enumerate(before): tape[i]=int(c)
        for i in range(len(before),len(before)+20): tape[i]=random.randint(0,1)
        ctx=dict(tape)
        r=run_to_F(tape, fpos_before)
        if r is None: return 'HALT'
        p,lo,hi,_=r
        if p!=fpos_after or lo< min(0,fpos_after) or hi>len(before)-1+0: return ('pos',p,lo,hi)
        for i,c in enumerate(after):
            if tape[i]!=int(c): return ('cell',i)
        for i in ctx:
            if (i<0 or i>=len(before)) and tape[i]!=ctx[i]: return ('ctx',i)
    return 'ok'
bad=0
# R1/R2: x [F] a 1 1 -> [F] x 1 a 0   (F at index 1 -> index 0)
for x in '01':
    for a in '01':
        r=check(x+a+'11',1, x+'1'+a+'0',0)
        if r!='ok': print('R1/R2',x,a,r); bad+=1
for m in range(0,41):
    r=check('11'+'001'*m+'0000',0,'0'+'110'*m+'1'+'1110',3*m+2)
    if r!='ok': print('R3',m,r); bad+=1
    if m==0: r=check('01000',0,'01110',0)
    else: r=check('01'+'001'*m+'000',0,'00'+'110'*(m-1)+'1'+'11110',3*m)
    if r!='ok': print('R4',m,r); bad+=1
print('bad',bad)
