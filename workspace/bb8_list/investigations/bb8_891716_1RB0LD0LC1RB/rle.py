import re
def rle(s):
    """compress maximal repeats of '01' and '10' (>=3 times)"""
    out=[];i=0
    while i<len(s):
        done=False
        for u in ('01','10'):
            j=i
            while s[j:j+2]==u: j+=2
            n=(j-i)//2
            if n>=3:
                out.append('(%s)^%d'%(u,n)); i=j; done=True; break
        if not done:
            out.append(s[i]); i+=1
    return ' '.join(out).replace('  ',' ')
