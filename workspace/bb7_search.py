"""Bounded exact BB7 state-split exploration. No cutoff is a halting proof."""
import json, time, collections, argparse
from sim import parse, fmt

CORE = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF'
T = parse(CORE)

def extract(tape, p):
    if not tape or max(tape) >= p or p-min(tape)>20000:
        return None
    s=''.join('1' if x in tape else '0' for x in range(min(tape),p))
    if not s.startswith('111') or not s.endswith('0011100'): return None
    v=s[3:-7]; pairs=[]
    while v:
        n=0
        while v.startswith('01'): n+=1; v=v[2:]
        pairs.append(n)
        if v:
            if not v.startswith('1'): return None
            v=v[1:]
    if len(pairs)<3 or pairs[-2]!=0 or any(x%3!=1 for x in pairs[:-2]+pairs[-1:]): return None
    return [(pairs[-1]-1)//3, [(x-1)//3 for x in pairs[-3::-1]]]

def run(table, cap=30000, minlevel=12, start=0):
    tape=set(); p=0; state=start; hits=[]; hread=[0,0]
    for step in range(cap):
        r=int(p in tape)
        if state==7: hread[r]+=1
        if state==0 and r==0 and p-1 not in tape and p-2 not in tape and p-3 in tape:
            b=extract(tape,p)
            if b and (not hits or b!=hits[-1]['B']):
                hits.append({'step':step,'B':b,'Hreads':hread.copy()})
                if len(b[1])>=minlevel:
                    return {'status':'B', 'steps':step,'hits':hits,'Hreads':hread}
        w,d,ns=table[state][r]
        if w: tape.add(p)
        else: tape.discard(p)
        p+=d; state=ns
        if state<0:return {'status':'halt','steps':step+1,'ones':len(tape),'hits':hits,'Hreads':hread}
    return {'status':'cutoff','steps':cap,'ones':len(tape),'hits':hits,'Hreads':hread}

def search(cap):
    out=[]; counts=collections.Counter(); t0=time.time()
    for src in range(7):
      for symbol in range(2):
        w,d,target=T[src][symbol]
        if target<0: continue
        for hr in range(2):
          orig=T[target][hr]
          for nw in range(2):
            for nd in [-1,1]:
              for nt in range(8):
                mut=(nw,nd,nt)
                if mut==orig:continue
                table=[row.copy() for row in T]+[T[target].copy()]
                table[src][symbol]=(w,d,7);table[7][hr]=mut
                r=run(table,cap)
                counts[r['status']]+=1
                if r['hits'] or (r['status']=='halt' and r['steps']>20000):
                    out.append({'split':[src,symbol,target,hr],'tm':fmt(table),**r})
      print('done',chr(65+src), dict(counts),'seconds',round(time.time()-t0,1),flush=True)
    payload={'core':CORE,'cap':cap,'candidates':out,'counts':dict(counts),'elapsed':time.time()-t0}
    with open('bb7_search_results.json','w') as f:json.dump(payload,f,indent=2)
    print('saved',len(out),'candidates',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cap',type=int,default=30000);a=ap.parse_args();search(a.cap)
