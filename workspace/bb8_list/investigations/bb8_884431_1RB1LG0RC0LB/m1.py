import sys
from fam import *
def rle(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        out.append(s[i]+'x'+str(j-i)); i=j
    return ' '.join(out)
def run(word,N=200000):
    m=M('0'+word,0,'B')
    while m.n<N:
        if not m.step(): return ('HALT',m.n)
        if m.q==1 and m.t[m.p]==0 and not any(m.t[:m.p]) and m.n>0:
            t=m.t; hi=len(t)-1
            while hi>m.p and t[hi]==0: hi-=1
            return (m.n, rle(''.join(map(str,t[m.p:hi+1]))))
    return ('TIMEOUT',)
for p in range(0,9):
    row=[]
    for q in range(0,13):
        r=run('00'+'1'*p+'0'+'1'*q)
        row.append(str(r[1]) if len(r)>1 and r[0]!='HALT' else str(r))
    print('p=%d'%p, ' ; '.join('q=%d:%s'%(q,x) for q,x in enumerate(row)))
