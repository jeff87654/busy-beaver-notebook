import sys, re
from val import *
m=sys.argv[1]
br=lambda R: bounce_round(m,'G',R,'01','10',pre='',maxev=400)
def cls(r,y):
    if r[0]=='H': return 'H'
    if len(r)<3: return str(r)[:20]
    x,yy,t=r
    g=re.fullmatch(r'(1?)((?:110)*)11',t)
    if not g or x!=2: return f'?{yy-2*y},{t[:12]}'
    return f'{yy-2*y if yy>2*y-5 else "y="+str(yy)},{len(g.group(1))},{len(g.group(2))//3 if len(g.group(2))<30 else str(len(g.group(2))//3*3-4*y)+"+4y/3"}'
for f in (0,1):
    for n in range(-1,4):
        row=[]
        for y in range(3,15):
            t=('1' if f else '')+'110'*max(n,0)+('11' if n>=0 else '')
            row.append(f'{y}:'+cls(br('0101'+'10'*y+t),y))
        print(f,n,' '.join(row))
