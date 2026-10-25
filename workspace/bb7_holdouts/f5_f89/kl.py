# K-list view: from lit 'ends M N D L' lines -> "step A | digits | tail" with run compression (u=10 coding, sep 0)
import sys,re
from dec import cells
def parse(s):
    s=s.strip('0')
    toks=[];i=0
    while i<len(s):
        n=0
        while s.startswith('10',i): n+=1; i+=2
        if n: toks.append(n); 
        if i<len(s):
            if s[i]=='0': toks.append('.'); i+=1
            elif s[i]=='1' and not s.startswith('10',i): toks.append('#'); i+=1
    return toks
def tolist(toks):
    # digits separated by '.', consecutive '.' = zero digits
    out=[];cur=None;i=0
    # returns raw sequence: numbers and '.' and '#'
    res=[];prev_sep=True
    for t in toks:
        if t=='.':
            if prev_sep: res.append(0)
            prev_sep=True
        elif t=='#': res.append('#'); prev_sep=False
        else: res.append(t); prev_sep=False
    return res
def comp(l):
    out=[];i=0
    while i<len(l):
        j=i
        while j<len(l) and l[j]==l[i]: j+=1
        out.append(f"{l[i]}" + (f"^{j-i}" if j-i>1 else '')); i=j
    return ' '.join(out)
if __name__=='__main__':
    for line in sys.stdin:
        p=line.split(None,3)
        if len(p)<4: print(line.strip()); continue
        s,h=cells(p[3]); print(p[0], comp(tolist(parse(s))))
