import re,sys,os,time
sys.argv=['x']
import shadow2
from fam import expand_list
line=[l for l in open('../runs/shadow_K282.txt').read().split('\n') if l.startswith('EV34 ')][0]
m=re.search(r'\| \[(.*?)\] r=(\d+) h=(\d+) t\[(.*?)\]',line)
c=dict(Q='',g=0,toks=expand_list(m.group(1)),r=int(m.group(2)),h=int(m.group(3)),tail=expand_list(m.group(4)))
t=time.time()
c2=shadow2.literal(shadow2.word_of_cfg(c))
print('result', None if c2 is None else (c2.get('halt') or (c2['r'],c2['h'],c2['tail'][:3])), 'time', time.time()-t)
