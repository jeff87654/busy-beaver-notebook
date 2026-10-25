import itertools,sys
from absys import step
Ps=['01','11','011','111','0111','1111','11101']
def INV(L,P,G):
    s=''.join(map(str,L))
    if '111' in s: return False
    if P=='1111' and (not L or L[-1]!=1): return False
    for i,g in enumerate(G):
        if g<2: return False
        if i>0 and g==3: return False
    if G and G[0]==3 and P in ('01','11','0111','11101','1111'): return False
    return True
bad=0
Lmax=int(sys.argv[1]); Gmax=int(sys.argv[2]); gv=[2,3,4,5,6,7]
for nl in range(Lmax+1):
  for L in itertools.product([0,1],repeat=nl):
    for P in Ps:
      for ng in range(Gmax+1):
        for G in itertools.product(gv,repeat=ng):
          if not INV(list(L),P,list(G)): continue
          try:
            r=step(list(L),P,list(G))
          except Exception as e:
            print('EXC',L,P,G,e); bad+=1; continue
          L2,P2,G2=r
          # drop gaps beyond those known? G2 fine
          if not INV(L2,P2,G2):
            bad+=1
            if bad<40: print('VIOL',L,P,G,'->',L2,P2,G2)
print('bad',bad)
