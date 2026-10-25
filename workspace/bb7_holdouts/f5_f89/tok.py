# tok.py WORDS : read lit 'ends' lines, tokenize cell string (leading/trailing zeros stripped) greedily by words
# WORDS like "011=s,01=u" ; repeated identical tokens compressed as tok^n ; unit runs as u^n
import sys
from dec import cells
words=[w.split('=') for w in sys.argv[1].split(',')]
side=sys.argv[2] if len(sys.argv)>2 else 'L'
for line in sys.stdin:
    p=line.split(None,3)
    if len(p)<4: print(line.strip()); continue
    s,h=cells(p[3])
    if side=='R': s=s[::-1]
    s=s.strip('0'); i=0; toks=[]
    while i<len(s):
        for w,n in words:
            if s.startswith(w,i): toks.append(n); i+=len(w); break
        else: toks.append(s[i]); i+=1
    out=[];k=0
    while k<len(toks):
        j=k
        while j<len(toks) and toks[j]==toks[k]: j+=1
        out.append(toks[k]+('^%d'%(j-k) if j-k>1 else '')); k=j
    print(p[0],p[1],p[2],' '.join(out))
