import idle, sys, subprocess, random, os
M='1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA'
MS=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
HERE=os.path.dirname(os.path.abspath(__file__))
random.seed(int(sys.argv[2])); n=int(sys.argv[1]); nh=0
odd=lambda a,b: 2*random.randint(a,b)+1
for it in range(n):
    L=random.randint(0,5)
    left=random.choice(['','10^1 11^1','10^3 11^1','10^%d 11^1'%odd(0,6)])
    toks=[left] if left else []
    for _ in range(L): toks+=['01^%d'%odd(0,4),'10^%d'%odd(0,4),'11^1']
    toks+=['01^%d'%odd(0,4),'10^%d'%odd(0,12)]
    init='A 0 | '+' '.join(toks)+' [01]\n'
    p=subprocess.Popen([MS,M,'2','2000000','p0','i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'pids.txt'),'a') as f: f.write('%d ms.exe\n'%p.pid)
    out,_=p.communicate(init); r=out.strip().splitlines()[-1] if out.strip() else 'EMPTY'
    if r.startswith('H') or r.startswith('IN') or r=='EMPTY': nh+=1; print(init.strip(),'->',r,flush=True)
print('total',n,'halts/other',nh)
