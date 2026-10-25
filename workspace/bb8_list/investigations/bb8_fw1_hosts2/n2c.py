import idle
def seg(p,q): return '01'*p+'10'*q
def enc(segs): return '11'.join(seg(p,q) for p,q in segs)
def blk(b):
    if len(b)%2: b='0'+b
    t=[b[i:i+2] for i in range(0,len(b),2)]
    o=[];i=0
    while i<len(t):
        j=i
        while j<len(t) and t[j]==t[i]: j+=1
        o.append(t[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(o)
def dec(b):
    if len(b)%2: b='0'+b
    t=[b[i:i+2] for i in range(0,len(b),2)]
    out=[];cur=[0,0];bad=[]
    for x in t:
        if x=='01': cur[0]+=1
        elif x=='10': cur[1]+=1
        elif x=='11': out.append(tuple(cur)); cur=[0,0]
        else: bad.append(x)
    out.append(tuple(cur))
    return ';'.join('%d,%d'%s for s in out)+(' BAD' if bad else '')
