import idle, sys, re
from sim import T
def build(segs):
    cells=[]
    for i,(p,q) in enumerate(segs):
        if i: cells+=[1,1]
        cells+=[0,1]*p+[1,0]*q
    return cells
segs=[tuple(map(int,x.split(','))) for x in sys.argv[1].split(';')]
show=sys.argv[2].split(',') if len(sys.argv)>2 else None
cells=build(segs); off=0; tape={i:c for i,c in enumerate(cells)}
pos=len(cells); tape[pos]=0; tape[pos+1]=1; q=0
def blk(cells):  # group into aligned 2-blocks from index 0
    return ' '.join(''.join(map(str,cells[i:i+2])) for i in range(0,len(cells),2))
for s in range(1,10**6):
    b=tape.get(pos,0); tr=T[(q,b)]
    if tr is None: print('HALT'); break
    tape[pos]=tr[0]; pos+=tr[1]; q=tr[2]
    hi=max(tape)+1
    right=''.join(str(tape.get(j,0)) for j in range(pos,hi+1)).rstrip('0')
    tag=None
    if q==0 and re.fullmatch(r'11((?:01)*)00((?:11)*)',right): tag='Wsep'
    if q==0 and re.fullmatch(r'00((?:11)*)',right): tag='Wre'
    if q==0 and right=='01': tag='K'
    if tag:
        left=[tape.get(j,0) for j in range(min(tape),pos)]
        print(s,tag,'pos%2=',pos%2,'| left blocks (from 0):',("[min=%d] " % min(tape)) + blk([tape.get(j,0) for j in range(min(tape)-(min(tape)%2),pos-(pos%2))]), ('+'+str(tape.get(pos-1,0)) if pos%2 else ''),'| right:',right)
        if tag=='K': break
