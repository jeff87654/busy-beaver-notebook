import sys,re,subprocess; sys.path.insert(0,'.'); from chk import TV,first
M='1RB0RG_1LC1RH_1LD0LB_0LE0LD_1RF1LD_0RA1LE_0RD0RE_1LG---'
ok=bad=0
for a in range(3,40,4):
  for b in range(3,40,3):
    r=first(M,'L','C','C',0,'0 10^%d 1 10^%d 110101'%(a,b),steps=10**7)
    exp='[C]0 (10)^%d 1 (10)^%d 1 1 0 1 0 1'%(a+4,b-2) if b-2>=3 else 'x'
    if r==exp: ok+=1
    elif exp!='x': bad+=1; print(a,b,r,exp)
print('inner ok',ok,'bad',bad)
# macro: n with suffix '1' -> after 5 rounds n'=32n+125 suffix '1'
res={}
for n in range(1,40):
    p=subprocess.Popen([TV,M,'3000000000','L:C','1','1','100000000','C','0','0 10^3 1 10^%d 1'%n],stdout=subprocess.PIPE,text=True)
    seq=[]; 
    for l in p.stdout:
      if l.startswith('HALT') or l.startswith('END'): seq.append(l.strip()[:30]); break
      if '|' in l:
        c=l.split('|',1)[1].strip(); mm=re.fullmatch(r'\[C\]0 \(10\)\^3 1 \(10\)\^(\d+) (.*)',c)
        if mm: seq.append((int(mm.group(1)),mm.group(2)))
        if len(seq)>=6: break
    p.kill(); res[n]=seq
    s5=seq[5] if len(seq)>5 else None
    print(n, 'n5=',s5, 'pred',32*n+125 if True else '', [x[1] if isinstance(x,tuple) else x for x in seq])
