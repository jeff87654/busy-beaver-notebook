from pathlib import Path
from sim import parse
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[9]);a,b=4,5
w='1111'+'01'*a+'0'+'1'*b+'01';t={i for i,c in enumerate(w) if c=='1'};p=len(w);q=7
for z in range(80):
 s=''.join(('['+chr(65+q)+':' if i==p else '')+str(int(i in t))+(']'if i==p else '')for i in range(-2,len(w)+12))
 print(z,s)
 wr,d,q=T[q][int(p in t)]
 if wr:t.add(p)
 else:t.discard(p)
 p+=d
 if q<0:break
