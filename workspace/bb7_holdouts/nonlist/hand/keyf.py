import sys, re
prev=None; n=0
for l in sys.stdin:
    if '|' not in l: print(l.strip()); continue
    a,b=l.split('|',1)
    k=re.sub(r'\[\d+\]','',b)
    k=re.sub(r'( 10(\^\d+)?)? 11(\^2)?( 01(\^\d+)?)?( 00)?\s*$','',k.rstrip())
    k=re.sub(r'\^\d+$','',k.strip())
    if k!=prev: print(l.strip()[:200]); prev=k; n+=1
