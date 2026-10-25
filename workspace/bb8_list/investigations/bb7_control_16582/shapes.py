import re,sys
lines=open(sys.argv[1]).read().splitlines()
prev=None
for ln in lines:
    m=re.match(r'^ +(\d+)  000\^inf (<[A-G] \(\d{3}\)) (.*) 000\^inf',ln)
    if not m: continue
    loop,head,rest=m.groups()
    blocks=re.findall(r'(\d{3})\^(\d+)',rest)
    # identify the big block
    if not blocks: continue
    exps=[int(e) for b,e in blocks]
    big=max(range(len(exps)),key=lambda i:exps[i])
    shape=head+' '+' '.join((b+'^X' if i==big else b+'^'+e) for i,(b,e) in enumerate(blocks))
    X=exps[big]
    d=len(str(X))
    print(loop, 'X~' + (str(X) if d<12 else f'{str(X)[:6]}e{d-1}'), shape)
