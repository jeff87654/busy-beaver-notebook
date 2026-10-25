import sys
from val import *
m=sys.argv[1]
br=lambda R: bounce_round(m,'G',R,'01','10',pre='',maxev=400)
bad=n=0
def ck(got,exp,tag):
    global bad,n
    n+=1
    if got!=exp:
        bad+=1
        if bad<8: print('MISMATCH',tag,str(got)[:80],'exp',str(exp)[:80])
for y in (2,3,4,5,9,21,45,100,201):
    for c in range(4,16):
        ck(br('0101'+'10'*y+'1'*c+'011'),(2,2*y+3,'1'*(c-2)+'011'),f'T{y},{c}')
        ck(br('0101'+'10'*y+'1'*c),(2,2*y+3,'1'*(c-2)),f'U{y},{c}')
    ck(br('0101'+'10'*y+'111011'),(2,2*y+4,'11'),f'T{y},3')
    ck(br('0101'+'10'*y+'11'),(2,3,'1'*(4*y+5)+'011'),f'U{y},2')
print(m,n,'cases',bad,'bad')
