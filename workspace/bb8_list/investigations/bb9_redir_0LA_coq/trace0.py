import sys
from tm_old import Sim, rle
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA'
def D(m): return '10'*m+'1'
def W(toks): return ''.join(D(t) for t in toks)
def start(toks,q='G'):
    w=W(toks); s=Sim(M,'0'*50+w,None,q); s.pos=50+len(w); s._grow(); return s
if __name__=='__main__':
    b=int(sys.argv[1]); ndig=int(sys.argv[2]) if len(sys.argv)>2 else 35
    s=start([1]*ndig+[1,3*b+1,2])
    ev=0
    while s.steps<5*10**7:
        q=s.q; c=s.t[s.pos]
        if (q,c) in (('E',0),('I',1),('I',0)):
            print(s.steps,q,c,s.view()[:300]); ev+=1
        if q=='G' and c==0 and ev>0 and s.t.rfind(1)<s.pos:
            v=s.view(); print('FAM',s.steps,v[:300])
            if 'D37' in v: break
        if not s.step(): print('halt',s.q,s.steps); break
