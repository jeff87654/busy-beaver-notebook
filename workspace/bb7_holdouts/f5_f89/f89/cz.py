# compress kl.exe output: tokens "# n # n ..." -> digit list with runs
import sys,re
every=int(sys.argv[1]) if len(sys.argv)>1 else 1
k=0
for line in sys.stdin:
    p=line.split()
    if not p or not p[0].isdigit(): print(line.strip()); continue
    k+=1
    if k%every: continue
    toks=p[1:]; out=[]; i=0
    while i<len(toks):
        j=i
        while j<len(toks) and toks[j]==toks[i]: j+=1
        out.append(toks[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
    # now compress repeated pairs "# x"
    s=' '.join(out)
    s=re.sub(r'((?:# \d+ ))\1{2,}',lambda m: '[%s]^%d '%(m.group(1).strip(),len(m.group(0))//len(m.group(1))),s+' ')
    print(p[0],s)
