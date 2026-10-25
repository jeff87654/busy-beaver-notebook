# ev.py MACHINE Q SIDE STEPS REGEX [COND] : run sim 'at' events, expand tape (left+'|'+right), match regex on full tape string
# prints step + group lengths (or group strings if short) for matches satisfying COND (python expr over g = list of lengths); non-matches as OTHER (compressed, truncated)
import sys,re,subprocess
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s2')
from val import expand
m,Q,S,N,rx=sys.argv[1:6]; cond=sys.argv[6] if len(sys.argv)>6 else 'True'
p=subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s2\sim.exe',m,N,'at',Q,S,'100000000'],stdout=subprocess.PIPE,text=True)
R=re.compile(rx); nother=0
for ln in p.stdout:
    mm=re.match(r'(\d+) (\w) \| (.*)<\w>(.*)$',ln)
    if not mm: continue
    t=expand(mm.group(3))+'|'+expand(mm.group(4))
    g=R.fullmatch(t)
    if not g:
        nother+=1
        if nother<=8: print('OTHER',mm.group(1),ln.split('|',1)[1].strip()[:140])
        continue
    G=[len(x) if x is not None else -1 for x in g.groups()]
    if eval(cond): print(mm.group(1),*G)
print('others',nother)
