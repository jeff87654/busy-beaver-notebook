import sys
sys.path.insert(0,'.')
from tm_old import Sim
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA'
def D(m): return '10'*m+'1'
def W(toks): return ''.join(D(t) for t in toks)
def run_until(toks, targets, maxsteps=10**7):
    w=W(toks); s=Sim(M,'0'*50+w,None,'G'); s.pos=50+len(w); s._grow()
    tw={W(t):t for t in targets}
    for i in range(maxsteps):
        if s.q=='G':
            st,l,r=s.word()
            if s.t[s.pos]==0 and r < s.pos:
                cur=st[l:s.pos]
                if cur in tw: return ('REACHED',tw[cur],s.steps)
        if not s.step(): return ('HALT',s.q,s.steps)
    return ('TIMEOUT',None,s.steps)
if __name__=='__main__':
    for r in (0,3,9):
      for m in (2,3,5):
        start=[9,9,8,3]+[1]*m+[1,r,4]
        t1=[9,9,8,0,2*r+7]+[1]*(m-1)+[1,0,4]
        t2=[9,9,8,0,2*r+4]+[4]*(m-2)+[1,37,18,4]
        print(r,m,run_until(start,[t1,t2]))
