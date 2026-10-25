from pathlib import Path
import json,sys
sys.set_int_max_str_digits(100000)
from rewrite import Rope,advance_fast,SymbolicStop
root=Path(__file__).parent
maxbits=int(sys.argv[1]) if len(sys.argv)>1 else 1000000
prefix='deep_' if len(sys.argv)>1 else ''
def encode(x):
    if isinstance(x,int) and x.bit_length()>20000:return {'hex':hex(x),'bits':x.bit_length()}
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x
def num(n):
    return str(n) if n.bit_length()<120 else f'<{n.bit_length()} bits, mod12={n%12}>'
def fmt(r):return ' '.join(f'({w})^{num(n)}' for w,n in r.d)
a=4;r=Rope([('110100100',1)]);t=189
with (root/(prefix+'fast_trace.txt')).open('w') as f:
    for i in range(10000):
        try:na,nr,dt,rule=advance_fast(a,r,maxbits)
        except SymbolicStop as e:
            data=e.data;data.update({'steps_before':t,'a':a,'tail':list(r.d),'iteration':i})
            (root/(prefix+'symbolic_frontier.json')).write_text(json.dumps(encode(data),indent=2))
            print('SYMBOLIC FRONTIER',i,'t',num(t),'a',a,'u',num(data['u']),'v',num(data['v']),'w',num(data['w']),'m',num(data['m']),file=f)
            print('suffix',fmt(Rope(data['suffix'])),file=f)
            print('SYMBOLIC FRONTIER',i,'m',num(data['m']),'v',num(data['v']),'w',num(data['w']))
            break
        t+=dt;a=na;r=nr
        if i<90 or rule.startswith('cycle') or rule in ('blank','reset000'):
            print(i,rule,'t',num(t),'a',num(a) if a is not None else 'HALT',fmt(r) if r else '',file=f)
        if a is None:print('HALT',num(t));break
