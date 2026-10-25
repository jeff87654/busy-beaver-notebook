import re,subprocess,os,sys
sys.argv=['x']
from fam import expand_list, spec_of_word, M
def word_of_cfg(c):
    w=''.join('10'*t+'1' for t in c['toks'])+'10'*c['r']+'1'*c['h']
    for x in c['tail']: w+='00'+'1'*x
    return w
line=[l for l in open('../runs/shadow_K282.txt').read().split('\n') if l.startswith('EV34 ')][0]
m=re.search(r'\| \[(.*?)\] r=(\d+) h=(\d+) t\[(.*?)\]',line)
c=dict(toks=expand_list(m.group(1)),r=int(m.group(2)),h=int(m.group(3)),tail=expand_list(m.group(4)))
w=word_of_cfg(c); spec=spec_of_word(w)
print('word len',len(w),'toks',len(c['toks']))
env=dict(os.environ,FSZ=str(1<<27),FSNAP_NOTRUNC='1')
p=subprocess.Popen([os.path.abspath('fsnap.exe'),M,spec,'3000000000','0','100000','60'],stdout=subprocess.PIPE,text=True,env=env)
n=0
for ln in p.stdout:
    n+=1
    print(ln[:230].rstrip())
    if n>=40: break
p.kill()
