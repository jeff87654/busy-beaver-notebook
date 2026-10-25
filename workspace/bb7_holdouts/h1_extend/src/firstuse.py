import sys
from lit import parse
for m in sys.argv[1:]:
    T=parse(m); tape={}; p=0; q=0; first={}
    for s in range(2000000):
        c=tape.get(p,0)
        if (q,c) not in first: first[(q,c)]=s
        tr=T[(q,c)]
        if tr is None: print('HALT',s); break
        tape[p]=tr[0]; p+=tr[1]; q=tr[2]
    print(m, ' '.join(f"{'ABCDEFG'[k[0]]}{k[1]}:{v}" for k,v in sorted(first.items(), key=lambda x:x[1])), 'unused:', [f"{'ABCDEFG'[k[0]]}{k[1]}" for k in T if k not in first])
