"""Search split-initializer contexts with every possible start state."""
import json,collections,time
from bb7_search import T,run,fmt

def start_table(table, start):
    order=[start]+[x for x in range(8) if x!=start]
    rev={s:i for i,s in enumerate(order)}
    return [[(w,d,rev.get(ns,-1)) for w,d,ns in table[s]] for s in order]

out=[];counts=collections.Counter();t0=time.time()
for src,symbol in [(2,0),(4,1)]:
    w,d,target=T[src][symbol]
    for nw in range(2):
      for nd in [-1,1]:
        for nt in range(8):
          mut=nw,nd,nt
          if mut==T[target][0]: continue
          table=[row.copy() for row in T]+[T[target].copy()]
          table[src][symbol]=(w,d,7);table[7][0]=mut
          for start in range(8):
            r=run(table,30000,start=start)
            counts[r['status']]+=1
            if r['hits']:
              out.append({'split':[src,symbol,target,0],'start':start,'tm':fmt(start_table(table,start)), 'original_labels_tm':fmt(table),**r})
    print('done',src,symbol,dict(counts),'seconds',time.time()-t0,flush=True)
json.dump({'cap':30000,'counts':dict(counts),'candidates':out,'elapsed':time.time()-t0},open('bb7_search_initial_results.json','w'),indent=2)
print('saved',len(out),'candidates',flush=True)
