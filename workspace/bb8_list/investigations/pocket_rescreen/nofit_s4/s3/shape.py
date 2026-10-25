# shape.py M N Q side unit : print events, tape with given unit word replaced by '#'
import sys,subprocess,re
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
from val import expand
M,N,Q,S=sys.argv[1:5]; units=sys.argv[5:]
p=subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s3\sim.exe',M,N,'at',Q,S,'10000000'],stdout=subprocess.PIPE,text=True)
for ln in p.stdout:
    m=re.match(r'(\d+) (\w) \| (.*) <\w> (.*)$',ln.strip())
    if not m: print(ln.strip()); continue
    t=expand(m.group(3))+'|'+expand(m.group(4))
    for i,u in enumerate(units): t=t.replace(u,'#ABCDEFG'[i])
    t=re.sub(r'(#+|A+|B+|C+)',lambda g:'%s^%d'%(g.group(1)[0],len(g.group(1))) if len(g.group(1))>2 else g.group(1),t)
    print(m.group(1),t[:220])
