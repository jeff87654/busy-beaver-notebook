import subprocess,sys,collections
import os
LIT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'src','lit.exe'))
def look(m,steps=3000000,n=6):
    out=subprocess.run([LIT,'ends',m,str(steps),'*','*','100000000'],capture_output=True,text=True).stdout.splitlines()
    ev=[l.split(' ',3) for l in out if l[0].isdigit()]
    c=collections.Counter((e[1],e[2]) for e in ev)
    (q,sd),k=c.most_common(1)[0]
    sel=[e for e in ev if e[1]==q and e[2]==sd]
    print('##',m,'events',len(ev),'top',q,sd,k, dict(c.most_common(4)))
    for e in sel[-n:]: print('  ',e[0],e[3][:180])
for m in sys.argv[1:]: look(m)
