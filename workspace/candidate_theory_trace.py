from sim import parse
T=parse(open('discovery_holdouts.txt').read().splitlines()[6]);tape=set(range(-9,0));p=0;st=7
for step in range(126):
 lo=min(tape|{p});hi=max(tape|{p});word=''.join('1'if i in tape else'0'for i in range(lo,hi+1))
 if (st in [5,7] and '0' not in word[:p-lo+1]) or step<24:
  print(step,chr(65+st),p-lo,word,flush=True)
 w,d,ns=T[st][int(p in tape)]
 if w:tape.add(p)
 else:tape.discard(p)
 p+=d;st=ns
