import re
def comp(t):
    o=[];i=0;n=len(t)
    while i<n:
        bp=bk=bc=0
        for p in range(1,9):
            if i+p>n: break
            k=1
            while i+(k+1)*p<=n and t[i+k*p:i+(k+1)*p]==t[i:i+p]: k+=1
            if k>=3 and k*p>bc: bc,bp,bk=k*p,p,k
        if bk>=3 and bc>=6:
            b=t[i:i+bp]; o.append((b if bp==1 else '('+b+')')+'^'+str(bk)); i+=bc
        else: o.append(t[i]); i+=1
    return ' '.join(o)
