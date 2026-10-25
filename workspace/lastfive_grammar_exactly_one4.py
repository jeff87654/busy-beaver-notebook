"""Falsification search for a proposed A-boundary grammar; observations are not proofs."""
import json,itertools,time
from pathlib import Path
from sim import parse
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[15]);out={'candidate':'C16','step_cap_per_word':20000,'results':[]};start=time.monotonic()
for k in range(6):
 for n in (3,4):
  for digits in itertools.product((2,3,4),repeat=k):
   if (n==4)+digits.count(4)!=1:continue
   word='1'*n+''.join('0'+'1'*r for r in digits)+'01';t={i for i,x in enumerate(word)if x=='1'};p=-1;s=0
   result={'n':n,'digits':digits,'status':'cutoff'}
   for step in range(20000):
    w,d,s=T[s][int(p in t)]
    if w:t.add(p)
    else:t.discard(p)
    p+=d
    if s<0:result.update(status='halt',steps=step+1);break
    if s==0 and p not in t and p==min(t)-1:
     ww=''.join('1'if q in t else'0'for q in range(p+1,max(t)+1));runs=[(c,len(list(g)))for c,g in itertools.groupby(ww)]
     good=all(c=='1' or m==1 for c,m in runs) and runs[0][1] in (3,4) and runs[-1]==('1',1) and all(m in(2,3,4)for c,m in runs[2:-1]if c=='1')
     good=good and sum(c=='1' and m==4 for c,m in runs)==1
     result.update(status='closed'if good else'outside_grammar',steps=step+1,output_runs=runs);break
   out['results'].append(result)
   if result['status'] in ('halt','outside_grammar'):
    print('COUNTEREXAMPLE',json.dumps(result),flush=True)
    # One short counterexample is sufficient to reject unrestricted grammar.
    out['elapsed_seconds']=time.monotonic()-start;Path('lastfive_grammar_exactly_one4.json').write_text(json.dumps(out,indent=2));raise SystemExit
out['elapsed_seconds']=time.monotonic()-start;Path('lastfive_grammar_exactly_one4.json').write_text(json.dumps(out,indent=2));print('done',len(out['results']),flush=True)
