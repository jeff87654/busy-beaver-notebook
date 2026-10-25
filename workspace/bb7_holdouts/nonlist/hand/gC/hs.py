"""hs.py MACHINEFILE K "SPEC with {a},{b}" MAXMACRO a_lo-a_hi b_lo-b_hi : idle; ms.exe exact; prints halts + summary."""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
mf,K,spec,mm,ar,br=sys.argv[1:7]; m=open(mf).read().strip()
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
def rng(s): a,b=s.split('-'); return range(int(a),int(b)+1)
nh=0; tot=0; ends=0
for a in rng(ar):
    for b in rng(br):
        line=subprocess.run([sys.executable,'ex.py',spec.format(a=a,b=b)],capture_output=True,text=True).stdout.strip()[2:]
        r=subprocess.run([ms,m,K,mm,'p0','i'],input=line+'\n',capture_output=True,text=True,creationflags=0x40).stdout.strip().splitlines()[-1]
        tot+=1
        if r.startswith('H'): nh+=1; print('HALT a=%d b=%d'%(a,b), r)
print('runs',tot,'halts',nh)
