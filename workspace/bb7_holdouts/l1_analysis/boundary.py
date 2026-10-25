from probe import Sim,compact

def run(a,tail,budget=100000):
 s=Sim(1,'0000'+'100'*a+tail,6)
 for i in range(budget):
  s.step()
  if s.halted: return ('HALT',s.steps,s.word())
  if s.q==6 and not s.L and s.cur==0:
   w=s.word()[1:].rstrip('0')
   assert w.startswith('000')
   w=w[3:]; n=0
   while w.startswith('100'):
    n+=1; w=w[3:]
   return (n,s.steps,w)
 return ('LIMIT',s.steps,None)
if __name__=='__main__':
 for tail in ['110'+'010'*4+'011'+'1100'*3+'101001','010'*4+'011'+'1100'*3+'101001','110'+'100'*2,'11100110011001100110011001100101001','01'+'100'*5+'1100'*3+'101001']:
  print('TAIL',compact(tail))
  for a in [2,3,4,5,6,7,8,9,10]:
   n,t,w=run(a,tail)
   print(a,n,t,compact(w) if w else w)
