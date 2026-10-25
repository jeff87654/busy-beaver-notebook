import idle,sys
from rules import *
M = M1 if sys.argv[1]=='1' else M2
print('Bk validity grid (rows k, cols a=1..30): . ok, X wrong')
for k in range(1,23):
    row=''
    for a in range(1,31):
        ds=[0]*k+[2,3]
        p=('K',(1,[1]*(k-1)+[3*a+3-k,1,3]))
        r=nextk(M,a,ds,maxs=4*10**5)
        row+= '.' if (r[0]=='K' and tuple(r[2])==(p[1][0],p[1][1])) else ('X' if r[0]!='TO' else 'T')
    print(f'k={k:2d} {row}')
print('E grid: H halt, other')
for k in range(1,23):
    row=''
    for a in range(1,31):
        r=nextk(M,a,[0]*k,maxs=4*10**5)
        row+= 'H' if r[0]=='HALT' else ('T' if r[0]=='TO' else 'K')
    print(f'k={k:2d} {row}')
