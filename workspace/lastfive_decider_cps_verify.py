"""Independent finite CPS certificate verifier: no imports from upstream CPS.
Checks blank-language inclusion, exact transitions on each finite window, and
all graph/configuration closure obligations. History is an explicit deterministic
annotation that erases to the original Turing machine.
"""
import json,sys
from pathlib import Path

def verify(c):
 machine=c['machine'];T=[]
 for row in machine.split('_'):
  assert len(row)==6
  T.append([(int(x[0]),1 if x[1]=='R'else 0,-1 if x[2]=='Z'else ord(x[2])-65)for x in(row[:3],row[3:])])
 for row in T:
  for w,d,s in row:assert w in(0,1)and d in(0,1)and -1<=s<len(T)
 mode=c['history'];b=c['block'];width=c['window'];assert b>=1 and width>=2*b
 assert mode=='lru'or type(mode)is int and mode>=0
 symbols=[]
 for base,h in c['symbols']:
  h=tuple(tuple(p)for p in h)
  assert base in(0,1)
  for s,w in h:assert 0<=s<len(T)and w in(0,1)
  if mode==0:assert not h
  elif mode=='lru':assert len(h)==len(set(h))
  else:assert len(h)<=mode
  symbols.append((base,h))
 assert len(set(symbols))==len(symbols)
 blank=c['blank_symbol'];assert symbols[blank]==(0,())
 def symwindow(ids):
  assert all(type(i)is int and 0<=i<len(symbols)for i in ids)
  return tuple(symbols[i]for i in ids)
 configs=set()
 for q in c['configs']:
  state=q['state'];direction=q['dir'];tape=symwindow(q['window']);pos=q['pos']
  assert 0<=state<len(T)and direction in(0,1)and len(tape)==width
  assert pos==(b-1 if direction==0 else width-b)
  configs.add((state,direction,tape,pos))
 assert len(configs)==len(c['configs'])
 edges=[{},{}]
 for direction,src,dst in c['edges']:
  assert direction in(0,1)
  src=symwindow(src);dst=symwindow(dst);assert len(src)==b and len(dst)==b
  edges[direction].setdefault(src,set()).add(dst)
 z=(symbols[blank],)*b
 for direction in(0,1):assert z in edges[direction].get(z,set())
 assert(0,1,(symbols[blank],)*width,width-b)in configs
 def get(tape,direction,index):
  start=index*b;end=(index+1)*b
  if direction==1:start,end=width-end,width-start
  return tape[start:end]
 total=0;local_loops=0;obligations=0
 for state,direction,old,pos in configs:
  tape=list(old);seen=set();s=state;d=direction
  while 0<=pos<width:
   key=(s,d,pos,tuple(tape))
   if key in seen:local_loops+=1;break
   seen.add(key)
   base,h=tape[pos];w,d,ss=T[s][base]
   if ss<0:raise ValueError('certificate includes a window that halts')
   if mode==0:hh=()
   elif mode=='lru':hh=((ss,w),)+tuple(p for p in h if p!=(ss,w))
   else:hh=(((ss,w),)+h)[:mode]
   tape[pos]=(w,hh);s=ss;pos+=1 if d==1 else-1
   total+=1
   if total>20000000:raise ValueError('verification cutoff: literal step budget')
  else:
   new=tuple(tape);behind=1-d
   far=get(new,behind,0);second=get(new,behind,1)
   assert far in edges[behind].get(second,set()),'missing newly adjacent blocks'
   obligations+=1
   for dst in edges[behind].get(get(old,behind,0),set()):
    assert dst in edges[behind].get(far,set()),'missing inherited trailing edge'
    obligations+=1
   for front in edges[d].get(get(old,d,0),set()):
    tape2=front+new[:width-b]if d==0 else new[b:]+front
    nxt=(s,d,tape2,b-1 if d==0 else width-b)
    assert nxt in configs,'missing successor configuration'
    obligations+=1
 return {'status':'independently_verified_nonhalting','configs':len(configs),'edges':sum(len(x)for m in edges for x in m.values()),'closure_obligations':obligations,'literal_steps':total,'local_exact_cycles':local_loops}

if __name__=='__main__':
 results=[]
 for p in map(Path,sys.argv[1:]):
  c=json.loads(p.read_text())
  try:r=verify(c)
  except Exception as e:r={'status':'rejected_or_inconclusive','reason':repr(e)}
  results.append({'certificate':str(p),**r})
 print(json.dumps(results,indent=2))
