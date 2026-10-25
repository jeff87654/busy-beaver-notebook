"""Bounded standalone Ligocki CPS portfolio; upstream files remain unchanged.
Fixed history is corrected locally: upstream Fixed_History_MM incorrectly calls
update_history_lru and ignores max_hist. The subclass below invokes the supplied
update_history_fixed routine. Any success is only a candidate until independently
checked from its exported finite graph.
"""
from pathlib import Path
import sys,json,time,subprocess,traceback,hashlib
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parent
CODE=ROOT/'third_party/ligocki/Code';DEPS=ROOT/'third_party/runtime_deps'
def child(p):
 sys.path[:0]=[str(CODE),str(DEPS)]
 import CPS,IO,io_pb2
 from Macro import Turing_Machine as TM
 class FixedHistory(TM.Fixed_History_MM):
  def get_trans_object(self,hs,state,dir):
   tr=self.base_tm.get_trans_object(hs.base_symbol,state,dir)
   pair=(tr.state_out,tr.symbol_out)
   return tr.replace(symbol_out=TM.update_history_fixed(hs,tr.symbol_out,pair,self.max_hist))
 base=IO.get_tm(p['machine']);mode=p['history']
 if isinstance(mode,int) and mode>0:tm=FixedHistory(base,mode)
 elif mode=='lru':tm=TM.LRU_History_MM(base)
 else:tm=base
 # Distinguish fixed-history from accidental LRU using repeated identical events.
 if isinstance(mode,int) and mode>0:
  hs=TM.History_Symbol(1,())
  for _ in range(mode+3):hs=tm.get_trans_object(hs,0,1).symbol_out
  assert len(hs.history)==mode and len(set(hs.history))==1
 result=io_pb2.CPSFilterResult()
 graph=CPS.CPSSim(tm,p['block'],p['window'],p['max_steps'],1000,p['max_configs'],p['max_edges'],result)
 t=time.monotonic();graph.run()
 conditions={}
 for tr,_ in graph.transitions.values():conditions[tr.condition]=conditions.get(tr.condition,0)+1
 out={**p,'status':'candidate_invariant'if result.success else'inconclusive','elapsed_engine_seconds':time.monotonic()-t,
      'counts':{'steps':result.num_steps,'iterations':result.num_iters,'configs':result.num_configs,'edges':result.num_edges},'abstract_transition_conditions':conditions}
 if result.success:
  symbols=[];ids={}
  def symbol(s):
   key=(int(s.base_symbol),tuple((int(a),int(b))for a,b in s.history))if isinstance(s,TM.History_Symbol)else(int(s),())
   if key not in ids:ids[key]=len(symbols);symbols.append([key[0],list(key[1])])
   return ids[key]
  def block(x):return[symbol(s)for s in x]
  blank_id=symbol(tm.init_symbol)
  configs=[{'state':int(c.state),'dir':c.dir,'window':block(c.window),'pos':c.pos}for c in graph.transitions]
  edges=[[d,block(src),block(dst)]for d,adj in graph.continuations.items()for src,dsts in adj.items()for dst in dsts]
  cert={'schema_version':1,'machine':p['machine'],'history':mode,'block':p['block'],'window':p['window'],
        'symbols':symbols,'blank_symbol':blank_id,'configs':configs,'edges':edges}
  path=ROOT/'lastfive_decider_cps_certificates'/f"{p['id']}_{p['setting']:02}.json";path.parent.mkdir(exist_ok=True)
  path.write_text(json.dumps(cert,separators=(',',':')));out['certificate']=str(path)
 return out

def job(p):
 t=time.monotonic()
 try:
  r=subprocess.run([sys.executable,__file__,'--child',json.dumps(p)],capture_output=True,text=True,timeout=p['timeout'])
  if r.returncode:return{**p,'status':'error','returncode':r.returncode,'log':(r.stdout+r.stderr)[-10000:]}
  out=json.loads(r.stdout);out['elapsed_seconds']=time.monotonic()-t;return out
 except subprocess.TimeoutExpired:return{**p,'status':'cutoff','reason':'external_wall_timeout','elapsed_seconds':time.monotonic()-t}
 except Exception:return{**p,'status':'error','log':traceback.format_exc()}

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--child':
  try:print(json.dumps(child(json.loads(sys.argv[2]))))
  except Exception:print(json.dumps({'status':'error','log':traceback.format_exc()}))
 else:
  machines=(ROOT/'discovery_holdouts.txt').read_text().splitlines();settings=[(h,b,3*b)for h in(0,1,2,4,8,'lru')for b in(1,2,3,4)]
  jobs=[{'id':f'C{c:02}','machine':machines[c-1],'setting':i,'history':h,'block':b,'window':w,'max_steps':1000000,'max_configs':20000,'max_edges':50000,'timeout':8}for c in(13,15)for i,(h,b,w)in enumerate(settings)]
  results=[];t=time.monotonic()
  def save():
   out={'engine':'Ligocki CPS, unchanged CPSSim; local FixedHistory correction','upstream_cps_sha256':hashlib.sha256((CODE/'CPS.py').read_bytes()).hexdigest(),
        'upstream_machine_sha256':hashlib.sha256((CODE/'Macro/Turing_Machine.py').read_bytes()).hexdigest(),
        'correction':'Fixed_History_MM.get_trans_object uses update_history_fixed(hs,write,(state_out,write),max_hist), instead of upstream erroneous update_history_lru.',
        'settings':[{'history':h,'block':b,'window':w}for h,b,w in settings],'elapsed_seconds':time.monotonic()-t,'results':results}
   (ROOT/'lastfive_decider_cps.json').write_text(json.dumps(out,indent=2))
  with ThreadPoolExecutor(max_workers=2)as pool:
   futures={pool.submit(job,p):p for p in jobs}
   for f in as_completed(futures):
    r=f.result();results.append(r);save();print(r.get('id'),r.get('setting'),r['status'],r.get('counts'),flush=True)
  print('completed',len(results),'seconds',time.monotonic()-t)
