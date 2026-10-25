import idle
from blk import follow_blocks, word_of
from nx import M1,M2
for M in (M1,M2):
  row=[]
  for n in range(1,9):
    s=''
    for b in range(0,n+1):
        out=follow_blocks(M,word_of([2,2*n+2,2*b+2]),3*10**6,10**9)
        e=out[-1]; s+=' b%d:%s'%(b,'H%d'%e[1] if e[0]=='H' else 'T')
    print(M[-6:],'n',n,s)
