# reach.py M N Q side regex : first literal event (Q at side extreme) whose right tape (trailing 0 stripped) fully matches regex
import sys,subprocess,re
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
from val import expand
M,N,Q,S,rx=sys.argv[1:6]; R=re.compile(rx)
p=subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s3\sim.exe',M,N,'at',Q,S,'100000000'],stdout=subprocess.PIPE,text=True)
for ln in p.stdout:
    m=re.match(r'(\d+) (\w) \| (.*) <\w> (.*)$',ln.strip())
    if not m: continue
    t=(expand(m.group(3))+expand(m.group(4)) if S=='L' else expand(m.group(4))[::-1]+expand(m.group(3))[::-1]).rstrip('0')
    g=R.fullmatch(t)
    if g: print('REACH',m.group(1),[len(x) for x in g.groups()]); p.kill(); break
