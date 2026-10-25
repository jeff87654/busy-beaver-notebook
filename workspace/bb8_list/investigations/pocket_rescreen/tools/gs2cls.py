import collections, sys
c=collections.Counter(); ex={}; out=open(sys.argv[2],'w',newline='\n')
for l in open(sys.argv[1]):
    parts=l.strip().split(' | '); st=parts[-1].split()[-2]
    sn=[p.split()[:4] for p in parts[1:]]
    nb=[int(s[2]) for s in sn]; g=[int(s[3].split(',')[0]) for s in sn]
    if st!='RUN' or not sn: k=st
    elif nb[-1]==0: k='NOGAP@2e9'
    elif nb[-1]==1: k='1GAP@2e9(gap %s)'%('const' if len(g)>1 and abs(g[-1]-g[-2])<=max(4,g[-2]//10) else 'changing')
    else: k='MULTI@2e9'
    c[k]+=1; ex.setdefault(k,l.strip()[:240]); out.write(parts[0]+'\t'+k+'\n')
for k,v in c.most_common(): print(v,k); print('   ',ex[k])
