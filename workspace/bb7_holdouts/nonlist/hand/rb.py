"""rb.py MACHINE K TEMPLATE MAXMACRO vals... : for each b, run TEMPLATE.format(b=b) and print the first left-end config
(group view) with >= 4 groups, or H."""
import subprocess, sys
m,K,tp,mm=sys.argv[1:5]
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
def groups(t):
    toks=[(x.split('^')+['1'])[:2] for x in t]
    gs=[[]]
    for s,n in toks:
        if s=='00':
            for _ in range(int(n)): gs.append([])
        else: gs[-1].append(s if n=='1' else s+'^'+n)
    gs=['.'.join(g) if g else '-' for g in gs]
    out=[];i=0
    while i<len(gs):
        j=i
        while j+1<len(gs) and gs[j+1]==gs[i]: j+=1
        out.append(gs[i] if j==i else f'[{gs[i]}]x{j-i+1}'); i=j+1
    return gs,out
for b in sys.argv[5:]:
    p=subprocess.Popen([ms,m,K,mm,'l0','i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    p.stdin.write(tp.format(b=b)+'\n'); p.stdin.close(); res='END'
    for l in p.stdout:
        if l.startswith('H'): res=l.strip(); break
        if not l.startswith('T'): continue
        a,s=l.split('|',1); t=s.split()[1:]
        gs,out=groups(t)
        if len(gs)>=5: res=a.split()[1]+' '+a.split()[3]+' : '+' | '.join(out); break
    p.kill(); print(b,res[:150])
