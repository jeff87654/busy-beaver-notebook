import re
def rle(s):
    # compress to 2-blocks runs
    out=[];i=0
    return s
def blocks(tape,pos,st,lo=None,hi=None):
    if lo is None: lo=min(min(tape),pos)
    if hi is None: hi=max(max(tape),pos)
    lo-= (lo%2)  # even alignment from origin
    cells=''.join(str(tape.get(i,0)) for i in range(lo,hi+2))
    return lo,cells
def comp(cells,k=2):
    bl=[cells[i:i+k] for i in range(0,len(cells),k)]
    out=[];
    for b in bl:
        if out and out[-1][0]==b: out[-1][1]+=1
        else: out.append([b,1])
    return ' '.join(b if n==1 else f'{b}^{n}' for b,n in out)
