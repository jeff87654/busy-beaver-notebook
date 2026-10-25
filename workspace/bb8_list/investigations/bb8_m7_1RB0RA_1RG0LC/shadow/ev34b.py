import re,sys,os,subprocess,time
sys.argv=['x']
import shadow2
from fam import expand_list, spec_of_word, M
line=[l for l in open('../runs/shadow_K282.txt').read().split('\n') if l.startswith('EV34 ')][0]
m=re.search(r'\| \[(.*?)\] r=(\d+) h=(\d+) t\[(.*?)\]',line)
c=dict(Q='',g=0,toks=expand_list(m.group(1)),r=int(m.group(2)),h=int(m.group(3)),tail=expand_list(m.group(4)))
w=shadow2.word_of_cfg(c)
spec=spec_of_word(w)
env=dict(os.environ,FSZ=str(1<<27))
t=time.time()
p=subprocess.Popen([os.path.abspath('fsnap.exe'),M,spec,'3000000000','3','1000000000'],stdout=subprocess.PIPE,text=True,env=env)
n=0
for ln in p.stdout:
    n+=1
    if n<=12 or ln.startswith('HALT') or ln.startswith('EDGE'): print(n, ln[:140].rstrip(), '...', ln[-120:].rstrip())
    if n>=60: break
print('lines',n,'rc',p.poll(),'time',time.time()-t)
p.kill()
