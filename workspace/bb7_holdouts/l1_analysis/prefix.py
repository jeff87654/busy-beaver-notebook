from boundary import run
for j in range(8):
 p=f'{j:03b}'
 for suffix in ['11001100101001','10010011001100101001']:
  tail=p+suffix
  print('TAIL',tail)
  for a in [2,3,4,5]:
   n,t,w=run(a,tail)
   print(a,n,t,w)
