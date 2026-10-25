import sys
from fhlit import *
from tm_old import Sim
def run3(M, T, r3, x=1, every=0, lim=5*10**7, show=True):
    w = W([9]*x + [8, T, 0] + [1]*M + [1, r3])
    s = Sim(M_, '0'*50+w, None, 'F'); s.pos = 50+len(w); s._grow()
    while s.steps < lim:
        q=s.q; c=s.t[s.pos]
        if show and (q,c) in (('E',0),): print(s.steps, q, c, s.view()[:200])
        if show and every and s.steps % every == 0: print(s.steps, s.view()[:200])
        if not s.step():
            st,l,r = s.word(); return (s.q, s.t[s.pos], s.steps, st.count('1'), s.view()[:250])
    return None
M_ = M
if __name__ == '__main__':
    a = list(map(int, sys.argv[1:4]))
    print(run3(*a))
