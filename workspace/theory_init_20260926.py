from sim import parse
T=parse('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF')
def extract(tape,p):
    if any(x>=p for x in tape): return None
    mn=min(tape, default=p)
    s=''.join('1' if x in tape else '0' for x in range(mn,p))
    if not s.startswith('111') or not s.endswith('0011100'):return None
    v=s[3:-7];pairs=[]
    while v:
        n=0
        while v.startswith('01'):n+=1;v=v[2:]
        pairs.append(n)
        if v:
            if not v.startswith('1'):return None
            v=v[1:]
    if len(pairs)<3 or pairs[-2]!=0 or any(x%3!=1 for x in pairs[:-2]+pairs[-1:]):return None
    return ((pairs[-1]-1)//3, [(x-1)//3 for x in pairs[-3::-1]])
for w in [0,1]:
 for d in [-1,1]:
  for init in range(7):
   tape={0} if w else set();p=d;st=init
   found=[]
   for step in range(300000):
    if st==0:
     b=extract(tape,p)
     if b and (not found or len(b[1])>found[-1][1]):
      found.append((step+1,len(b[1]),b))
      if len(b[1])>=12:break
    e=T[st][int(p in tape)]
    if e is None:break
    ww,dd,ss=e
    if ww:tape.add(p)
    else:tape.discard(p)
    p+=dd;st=ss
    if st==-1:break
   print(w,d,chr(init+65),found[-3:], 'stop',step+1,st,len(tape))

