import idle
from predict import predict
from rules import nextk
from rsim import kconfig
from sim import M1,M2
def rule_run(a,ds,w):
    tot=0
    while True:
        p=predict(a,ds,w)
        if p[0]=='BAD': return ('BAD',)
        tot+=p[1]
        if p[0]=='HALT': return ('HALT',tot,p[2])
        a,ds=p[2]
for w,M in ((1,M1),(2,M2)):
    for a,ds in ((1,[0,1]),(2,[0,1]),(1,[3]),(1,[0,0,0]),(2,[1,0,0,0,0]),(3,[0]*9),(1,[0,0,1,0])):
        rr=rule_run(a,ds,w)
        r=kconfig(M,a,ds)
        while r.step(): pass
        print(w,a,ds,'rule:',rr,'literal(rsim):',r.steps,r.ones(), 'OK' if rr[1:]==(r.steps,r.ones()) else 'MISMATCH')
