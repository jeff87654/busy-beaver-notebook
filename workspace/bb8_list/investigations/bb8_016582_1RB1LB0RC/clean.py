import sys,re
from absys import step
c=int(sys.argv[1]); j=int(sys.argv[2])
L=[1,1,0]*c+[1]; P='1111'; G=[2]*j
L=[0]*0+L
i=0
while True:
    s=''.join(map(str,L)).lstrip('0')
    m=re.fullmatch(r'((?:110)*)(1|11|)',s)
    if m: print(i, len(m.group(1))//3, m.group(2) or '-', P, G)
    if P=='1111' and len(G)>j and s=='' : break
    try: L,P,G=step(L,P,G)
    except Exception as e: print('EXC',e);break
    i+=1
    if i>200000: break
    if P=="1111" and m and len(m.group(1))//3==c-1 and G==[2]*(j+1): print("DONE",i);break
