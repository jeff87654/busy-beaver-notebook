exec(open('theory_init_20260926.py').read().split('for w in [0,1]:')[0])
def bword(a,vec):return '111'+''.join('01'*(3*v+1)+'1' for v in vec[::-1])+'1'+'01'*(3*a+1)+'0011100'
def run(s,limit,blank=False):
 tape={i-len(s) for i,c in enumerate(s) if c=='1'};p=0;st=0;cov=set()
 for step in range(limit):
  if step and st==0 and extract(tape,p):break
  r=int(p in tape);w,d,ss=T[st][r]
  if w:tape.add(p)
  else:tape.discard(p)
  p+=d;cov.add((st,r,int(p in tape)));st=ss
  if st==-1:break
 return cov,step+1
coverage=set()
for a in range(4):
 for k in range(5):
  for n in range(3):
   for tail in [[],[0],[1],[0,2]]:
    cov,_=run(bword(a,[0]*k+[n]+tail),100000);coverage|=cov
init,_=run('',100000)
print('B macro context coverage:',sorted((chr(s+65),r,t) for s,r,t in coverage))
print('Init only contexts:',sorted((chr(s+65),r,t) for s,r,t in init-coverage))
print('Potential absent contexts:',sorted((chr(s+65),r,t) for s in range(7) for r in [0,1] for t in [0,1] if(s,r,t)not in coverage))
