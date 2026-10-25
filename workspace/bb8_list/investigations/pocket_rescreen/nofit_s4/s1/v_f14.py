import sys, re
from val import *
m0=sys.argv[1]
m='_'.join(''.join(t[i:i+3].replace('L','x').replace('R','L').replace('x','R') for i in (0,3)) for t in m0.split('_'))
br=lambda R: bounce_round(m,'A',R,'01','10',pre='0',maxev=400)
bad=n=0
def ck(got,exp,tag):
    global bad,n
    n+=1
    if got!=exp:
        bad+=1
        if bad<8: print('MISMATCH',tag,str(got)[:80],'exp',str(exp)[:80])
for y in range(2,14):
    for c in range(1,12):
        ck(br('00101'+'10'*y+'1'+'10'*c+'1'),(2,2*y+3,'1'+'10'*(c-1)+'1'),f'X{y},{c}')
ends={}
for y in range(2,40):
    for tail in ('11','1'):
        r=br('00101'+'10'*y+tail)
        ends.setdefault(tail,[]).append((y,r[:2],(lambda t: (len(t)-2)//2 if re.fullmatch(r'1(10)*1',t) else t[:20])(r[2]) if len(r)>2 else ''))
print(m0,n,'cases',bad,'bad')
for t,v in ends.items(): print(t, ' '.join(f'{y}:{a}/{c}' for y,a,c in v[:20]))
