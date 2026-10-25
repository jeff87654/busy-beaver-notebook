import re,sys
prev=None; prevline=None; cnt=0
for ln in open(sys.argv[1]):
    loop,rest=ln.rstrip('\n').split(' ',1)
    m=re.match(r'^0? ?\[([A-G])0\] (.*)$',rest)
    if not m: continue
    st,body=m.groups()
    toks=body.split()
    # find big run
    shape=st+' '+' '.join(re.sub(r'^([SD])\d+$',r'\1#',t) for t in toks)
    if shape!=prev:
        if prevline and cnt>1: print('   ...(%d similar) last:'%cnt, prevline)
        print(loop, st, body)
        cnt=0
    prev=shape; prevline=loop+' '+st+' '+body; cnt+=1
