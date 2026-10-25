"""Exact C16 macro run looking specifically for a failure of the observed E0 guard."""
import time,json
from pathlib import Path
from collections import Counter
from lastfive_family_map_reducer import macro,MACHINE
p=0;s='A';t=set();steps=0;counts=Counter();start=time.monotonic();event=None
for k in range(20_000_000):
 if s=='E' and p not in t and p-1 in t:
  event={'reason':'E0_left_neighbor_one','steps':steps,'head':p,'left_two_bits':str(int(p-2 in t))+'1','local_tape':''.join('1'if x in t else'0'for x in range(p-16,p+17))};break
 p,s,n,name=macro(t,p,s);steps+=n;counts[name]+=1
 if s=='Z':event={'reason':'halt','steps':steps};break
 if k%1024==0 and time.monotonic()-start>60:break
out={'machine':MACHINE,'candidate':'C16','engine':'independently crosschecked exact A/E/H macro rules','status':'guard_counterexample'if event else'cutoff','event':event,'steps':steps,'macro_operations':k+1,'elapsed_seconds':time.monotonic()-start,'rule_counts':counts,'checkpoint':{'state':s,'head':p,'ones':sorted(t)},'nonhalting_claim':False}
Path('lastfive_c16_guard_search.json').write_text(json.dumps(out,indent=2));print(json.dumps({key:out[key]for key in out if key!='checkpoint'}),flush=True)
