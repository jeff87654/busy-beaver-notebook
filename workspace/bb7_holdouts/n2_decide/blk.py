import idle
from sim import T
S='ABCDEFG'
# simulate inside a single 2-block until exit; entry at cell 0 (from left) or cell 1 (from right)
def run(q,blk,pos):
    b=list(blk); steps=0
    while 0<=pos<=1:
        tr=T[(q,b[pos])]
        if tr is None: return ('HALT',''.join(map(str,b)),steps)
        b[pos]=tr[0]; pos+=tr[1]; q=tr[2]; steps+=1
        if steps>50: return ('LOOP',)
    return ('R' if pos==2 else 'L', S[q], ''.join(map(str,b)), steps)
for entry,pos in (('from-left',0),('from-right',1)):
    print(entry)
    for q in range(7):
        row=[]
        for blk in ((0,0),(0,1),(1,0),(1,1)):
            r=run(q,blk,pos)
            row.append('%s%s:%s'%(*map(str,blk),) if False else ''.join(map(str,blk))+'->'+(' '.join(map(str,r[:3]))))
        print(' ',S[q],' | '.join(row))
