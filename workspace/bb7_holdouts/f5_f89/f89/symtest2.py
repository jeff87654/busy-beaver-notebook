from symtest import *
import symtest
H=('H',1); H2=('H',1,2)
T=[]
for a in range(1,22,2):
    for r in ([],[H],[1,H],[H2,1]):
        for zr in (0,1):
            T.append(('Bz a=%d'%a,[a,1,('Z',zr),H2]+r, lambda v: [Lin.c(1),('Z',v[2][1]),v[0]+4,v[3]-2]+v[4:]))
    for zr in (0,1):
        T.append(('Tz a=%d'%a,[a,1,('Z',zr),1], lambda v: [Lin.c(1),('Z',v[2][1]),v[0]+4]))
bad=0
for name,digs,f in T:
    vals=build(digs); exp=f(vals); got,verd=first_p1(digs)
    if got is None or not eq(got,exp): bad+=1; print('FAIL',name,digs,'got',show(got) if got else verd)
print('tests',len(T),'fail',bad)
