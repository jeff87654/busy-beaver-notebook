import sys,re
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); N=int(sys.argv[4])
s=tr.start(ds,a,b)
pat=re.compile(r'^11(101)+0?$')
while s.steps<N:
    if not s.step(): break
    if ST[s.state]=='C':
        t=s.tape; lo,hi=s.bounds()
        w=''.join(map(str,t[lo:hi+1]))
        if s.pos-lo==1 and re.match(r'^11(?:101)+$',w):
            print(s.steps,'E0 with t=',(len(w)-2)//3, w[:20]); break
        if s.pos-lo==1 and re.match(r'^11(?:101)+0*$',w):
            print(s.steps,'E0~ ',w[:30]); break
