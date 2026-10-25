from val import run
import sys
ms = [l.split('\t')[1].strip() for l in open('machines.txt') if l.strip()]
grp = [m for m in ms if True]
def cases():
    return [('B','10'*n+'1','',  '10'*(2*n+2)+'10', n) for n in range(1,151)]
for m in sys.argv[1:]:
    ok,bad,res = run(m,'B','R',cases(),'(10)+10')
    print(m, ok, bad, [r for r in res if not r[1]][:3])
