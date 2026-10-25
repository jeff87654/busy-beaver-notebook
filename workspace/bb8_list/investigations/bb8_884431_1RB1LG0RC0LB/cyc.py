import re
from fam import *
for b in range(0,8):
    m=kstart([],0,b)
    while m.n<300000:
        if not m.step(): print('HALT'); break
    w,p=m.word()
    mt=re.fullmatch(r'(1+)00(1+)',w)
    print(b,m.n,ST[m.q],'word shape', (len(mt.group(1)),len(mt.group(2))) if mt else w[:60],'head offset from end',len(w)-p)
