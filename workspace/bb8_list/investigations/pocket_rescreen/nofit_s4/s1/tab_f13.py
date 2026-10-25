import sys, re
from val import *
m=sys.argv[1]
br=lambda R: bounce_round(m,'G',R,'01','10',pre='',maxev=400)
def cls(r,y):
    if r[0]=='H': return 'H'
    if len(r)<3: return str(r)[:20]
    x,yy,t=r
    g=re.fullmatch(r'(1*)(011)?',t)
    if not g or x!=2: return f'?{x},{yy},{t[:15]}'
    k='T' if g.group(2) else 'U'
    return f'{k}({yy}-2y={yy-2*y},c={len(g.group(1))}{"" if len(g.group(1))<10 else "="+str(len(g.group(1))-4*y)+"+4y"})'
for kind,suf in (('T','011'),('U','')):
    for c in range(0,4):
        row=[]
        for y in range(3,12):
            row.append(f'{y}:'+cls(br('0101'+'10'*y+'1'*c+suf),y))
        print(kind,c,' '.join(row))
