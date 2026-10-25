import re
def tokview(bits):
    """greedy: P=11 optional then D(m)=(10)^m 1 tokens; other chars shown raw. Return list of strings"""
    out=[]; i=0; n=len(bits)
    if bits.startswith('11'):
        out.append('P'); i=2
    while i<n:
        m=0
        j=i
        while bits[j:j+2]=='10': j+=2; m+=1
        if m>=1 and bits[j:j+1]=='1':
            out.append(m); i=j+1
        elif m>=1:
            out.append('r%d'%m); i=j
        else:
            out.append('<'+bits[i]+'>'); i+=1
    # merge raw chars
    res=[]
    for t in out:
        if isinstance(t,str) and t.startswith('<') and res and isinstance(res[-1],str) and res[-1].startswith('<'):
            res[-1]=res[-1][:-1]+t[1]+'>'
        else: res.append(t)
    return res
def rl(toks):
    out=[];i=0
    while i<len(toks):
        j=i
        while j<len(toks) and toks[j]==toks[i]: j+=1
        out.append(str(toks[i]) if j-i==1 else '%s^%d'%(toks[i],j-i)); i=j
    return ' '.join(out)
if __name__=='__main__':
    import sys
    print(rl(tokview(sys.argv[1])))
