"""hscan.py MACHINE K TEMPLATE MAXMACRO a_range b_range : TEMPLATE with {a},{b}; reports H or END for each (a,b)."""
import subprocess, sys, itertools
m,K,tp,mm,ar,br=sys.argv[1:7]
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
def rng(s): a,b=s.split('-'); return range(int(a),int(b)+1)
for a in rng(ar):
    row=[]
    for b in rng(br):
        line=tp.format(a=a,b=b)
        r=subprocess.run([ms,m,K,mm,'p0','i'],input=line+'\n',capture_output=True,text=True,creationflags=0x40).stdout.strip().splitlines()[-1]
        row.append('H%s'%r.split('macro=')[1].split()[0] if r.startswith('H') else '.')
    print(a,' '.join(row))
