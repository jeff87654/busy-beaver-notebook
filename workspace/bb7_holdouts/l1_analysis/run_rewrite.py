from rewrite import Rope,advance
import sys,json
sys.set_int_max_str_digits(100000)
def num(n):
 if n.bit_length()<100:return str(n)
 return f'<{n.bit_length()} bits; mod12={n%12}>'
def fmt(r):return ' '.join(f'{w}^{num(n)}' for w,n in r.d)
a=4;tail=Rope([('110100100',1)]);t=189
with open('bb7_holdouts/l1_analysis/rewrite_trace.txt','w') as f:
 for i in range(50000):
  if i<150 or tail.peek(3)=='000' or i%1000==0:
   print(i,'t',num(t),'a',num(a),fmt(tail),file=f,flush=True)
  a,tail,dt,r=advance(a,tail);t+=dt
  if a is None:print('HALT',num(t),file=f);break
  if a.bit_length()>100000:print('BIG',file=f);break
 print('DONE',i,'a',num(a),'t',num(t), 'parts',len(tail.d) if tail else None)

