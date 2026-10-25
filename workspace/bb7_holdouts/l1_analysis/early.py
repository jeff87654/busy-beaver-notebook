from probe import Sim,compact
s=Sim(12)
i=0
with open('bb7_holdouts/l1_analysis/early.txt','w') as f:
 while s.steps<300000:
  if s.q==6 and not s.L and s.cur==0:
   w=''.join(format(b,'012b')*n for b,n in reversed(s.R)).rstrip('0')
   print(s.steps,compact(w),file=f)
  s.step()
