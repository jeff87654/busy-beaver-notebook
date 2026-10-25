# odd-mode abstract engine for F89. config = list of odd digits [a, d2, ..., dn] (separator-before coding)
def step(c):
    if any(x%2==0 for x in c): return None, 'EVEN'
    a=c[0]
    if len(c)==1: return [1]*(a+2), 'S'
    if c[1]>=3: return [a+4, c[1]-2]+c[2:], 'D'
    k=1
    while k+1<len(c) and c[k+1]==1: k+=1
    # c[1..k] are 1
    if k+1<len(c):
        d=c[k+1]; return [1]+[1]*(k-1)+[a+4, d-2]+c[k+2:], 'B%d'%k
    # all zeros to the top
    if k==1: return [a+4], 'T1'
    return [1]+[1]*(k-2)+[a+4], 'T'
