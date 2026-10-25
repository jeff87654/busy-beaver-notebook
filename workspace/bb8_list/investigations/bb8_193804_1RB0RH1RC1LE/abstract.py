import sys
def step(m, W):
    """one macro-step on (m, W) following R1 / R3 / R4 / R4e"""
    if W and W[0] >= 1:
        return m+1, [W[0]-1]+W[1:]
    j=0
    while j<len(W) and W[j]==0: j+=1
    if j==len(W):
        return 0, W+[4*m+4]
    W2=W[:]; W2[j]-=1; W2[j-1]=4*m+4
    return 0, W2
if __name__=='__main__':
    m,W=2,[]
    import time
    N=int(sys.argv[1])
    rounds=0
    mx=0
    for i in range(N):
        m,W=step(m,W)
        if i<40 or i%(N//12)==0:
            print(i,m,len(W),(W if len(W)<8 else W[:4]+['...']+W[-3:]))
