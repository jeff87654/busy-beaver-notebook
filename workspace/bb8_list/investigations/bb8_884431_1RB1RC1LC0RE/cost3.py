from grid1 import nxt
for k in range(0,5):
    row=[]
    for b in range(0,5):
        L=[0]*(k+1)+[2]
        r = nxt(L,0,b)
        row.append(r[0])
    print('k=%d (k+1 zeros)'%k, row)
