# parse kl.exe U=01 output; separator-before convention: tape = 00 [1 (01)^d1][1 (01)^d2]...  -> (pre, digits)
import sys
def parse(toks):
    i=0
    while i<len(toks) and toks[i]=='#': i+=1
    pre=i; digs=[]; cur=0
    for t in toks[i:]:
        if t=='#': digs.append(cur); cur=0
        elif t=='.': return pre,None
        else: cur=int(t)
    digs.append(cur)
    return pre,digs
def rl(d):
    if d is None: return 'BAD'
    out=[];i=0
    while i<len(d):
        j=i
        while j<len(d) and d[j]==d[i]: j+=1
        out.append(str(d[i])+('^%d'%(j-i) if j-i>1 else ''));i=j
    return ' '.join(out)
if __name__=='__main__':
    for line in sys.stdin:
        p=line.split()
        if not p or not p[0].isdigit(): print(line.strip()); continue
        pre,d=parse(p[1:])
        print(p[0],pre,'|',rl(d))
