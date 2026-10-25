import idle, subprocess, random, itertools
# verify K-level rules on grids; k2k prints next K config
random.seed(7)
def odd(): return random.choice([1,3,5,7])
def pref():
    k=random.randint(0,3); return [(odd(),odd()) for _ in range(k)]
cases=[]  # (input list, expected list)
def S(l): return ';'.join('%d,%d'%t for t in l)
for x in range(0,8):
  for y in range(0,8):
    L=pref(); cases.append(('R1',L+[(x+2,y)], L+[(x,y+4)]))
for p in range(0,6):
  for q in range(0,6):
    for j in range(0,4):
      for y in range(0,7):
        L=pref()
        cases.append(('R2',L+[(p,q+2)]+[(1,1)]*j+[(1,y)], L+[(p,q),(y+4,1)]+[(1,1)]*j))
        cases.append(('R6a',L+[(p,q+2)]+[(1,1)]*(j+1)+[(0,y)], L+[(p,q),(y+2,1)]+[(1,1)]*j+[(0,3)]))
        cases.append(('R6b',L+[(p,q+2),(0,y)], L+[(p,q),(y+1,3)]))
      for j in range(0,4):
        for y in range(0,7):
          L=pref()
          cases.append(('R3',L+[(p+2,1)]+[(1,1)]*j+[(1,y)], L+[(p,y+4)]+[(1,1)]*(j+1)))
          cases.append(('R7',L+[(p+2,1)]+[(1,1)]*j+[(0,y)], L+[(p,y+2)]+[(1,1)]*j+[(0,3)]))
for j in range(0,6):
  for y in range(0,12):
    if y%2==1: cases.append(('R4',[(1,1)]*j+[(1,y)], [(0,1)]+[(1,1)]*(j+(y+1)//2)+[(0,3)]))
    cases.append(('R8a',[(0,1)]+[(1,1)]*(j+1)+[(0,y)], [(y+3,1)]+[(1,1)]*j+[(0,3)]))
  cases.append(('R8b',[(0,1),(0,j)], [(j+2,3)]))
out=subprocess.run(['./k2k.exe','50000000','1'],input='\n'.join(S(c[1]) for c in cases)+'\n',capture_output=True,text=True,creationflags=0x40).stdout.split('\n')
res={}
i=0; idx=-1; got={}
for l in out:
    if l.startswith('IN'): idx+=1; got[idx]=None
    elif 'K step' in l: got[idx]=l.split(':')[1].strip()
    elif l.strip(): got[idx]='ERR '+l.strip()[:80]
from collections import Counter
ok=Counter(); bad=Counter(); ex={}
for n,c in enumerate(cases):
    if got.get(n)==S(c[2]): ok[c[0]]+=1
    else:
        bad[c[0]]+=1; ex.setdefault(c[0],[]).append((S(c[1]),got.get(n),S(c[2])))
for r in sorted(set(c[0] for c in cases)):
    print(r,'ok',ok[r],'bad',bad[r])
    for e in ex.get(r,[])[:6]: print('    in',e[0],'got',e[1],'exp',e[2])
