from fam_b import *
n=C(0,n=1); p=C(0,p=1); qq=C(0,q=1)
L=toks([('01',C(3,n=1))],left=True)
R=toks([('10',C(2,p=1)),('11',1),('01',C(2,q=1)),('00',1),('10',1),('01',1),('00',1),('10',1)])
start=('A',L,R,'>')
def tgt(cfg): return cfg[0]=="A" and cfg[1]!=L
script,end=P.drive('S0',start,tgt,matchers=[m_loop],maxev=200,verbose=True)
print(P.show(end))
