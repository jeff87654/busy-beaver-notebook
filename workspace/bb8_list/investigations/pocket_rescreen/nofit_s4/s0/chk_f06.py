import sys,re,subprocess; sys.path.insert(0,'.'); from chk import TV
Ms=['1RB---_1RC1LD_1LD1LF_1RG0LE_1LC1LB_0RA1LC_1RE1RH_0RF1RD','1RB---_1RC0RF_1LD1LF_1RG0LE_1LC1LB_0RA1LC_1RE1RH_0RF1RD']
for M in Ms:
  ok=bad=0
  for m in range(3,301,3):
    p=subprocess.Popen([TV,M,'2000000000','L:C','1','1','100000000','C','0','0 1^%d'%m],stdout=subprocess.PIPE,text=True)
    res=None
    for l in p.stdout:
      if l.startswith('HALT'): res=l.strip(); break
      if '|' in l:
        c=l.split('|',1)[1].strip(); mm=re.fullmatch(r'\[C\]0 \(1\)\^(\d+)',c)
        if mm: res=int(mm.group(1)); break
    p.kill()
    if res==18*m+63: ok+=1
    else: bad+=1; print(m,res)
  print(M,'ok',ok,'bad',bad)
