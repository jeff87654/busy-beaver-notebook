from sim import parse
T=parse('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF')
def bword(a,vec):return '111'+''.join('01'*(3*v+1)+'1' for v in vec[::-1])+'1'+'01'*(3*a+1)+'0011100'
for a in range(3):
 for k in range(3):
  s=bword(a,[0]*k);tape={i-len(s) for i,c in enumerate(s) if c=='1'};p=0;st=0;edges=set();steps=0
  while st!=-1 and steps<100000:
   r=int(p in tape);edges.add((st,r));w,d,ns=T[st][r]
   if w:tape.add(p)
   else:tape.discard(p)
   st=ns;p+=d;steps+=1
  mn=min(tape);mx=max(tape)
  out=''.join(('(' if i==p else '')+('1' if i in tape else '0')+(')' if i==p else '') for i in range(mn,mx+1))
  print(a,k,steps,'head',p-mn,'ones',len(tape),'out',out,'edges',sorted(edges))
