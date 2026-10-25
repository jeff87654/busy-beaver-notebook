import subprocess,sys,itertools,os
which=sys.argv[1]
M={'1':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_---0RF_---1RE','2':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE'}[which]
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\neighbors\probe2.exe'
env=dict(os.environ); env['PATH']=r'C:\msys64\ucrt64\bin;'+env['PATH']
def pred(ds,a,b):
    ds=list(ds)
    if a>=1: return (ds,a-1,2*b+2)
    if not any(ds):
        return ([2]+[0]*(12*b+len(ds)+3),0,0)
    # trailing zeros
    k=0
    while ds[-1]==0: ds.pop(); k+=1
    y1=ds.pop()
    if k==0: return (ds+[y1-1],2*b+2,0)
    return (ds+[y1-1,2*b+2]+[0]*(k-1),0,0)
def parse(line):
    import re
    m=re.match(r'K\((.*?); (\d+); (\d+)\) -> (.*)',line)
    ds=[int(x) for x in m.group(1).split(',')] if m.group(1) else []
    rest=m.group(4)
    if rest.startswith('K('):
        m2=re.match(r'K\((.*?); (\d+); (\d+)\) in (\d+)',rest)
        ds2=[int(x) for x in m2.group(1).split(',')] if m2.group(1) else []
        return ds,int(m.group(2)),int(m.group(3)),(ds2,int(m2.group(2)),int(m2.group(3)),int(m2.group(4)))
    return ds,int(m.group(2)),int(m.group(3)),rest
cases=[]
def add(ds,a,b): cases.append((tuple(ds),a,b))
for a in range(0,3):
  for b in range(0,7):
    for L in range(0,4):
      for ds in itertools.product(range(0,4),repeat=L):
        add(ds,a,b)
# deep zero tails
for b in range(0,9):
  for k in range(1,13):
    for pre in ([],[1],[2,1],[0,3],[1,0,2]):
      for y in (1,2,3):
        add(pre+[y]+[0]*k,0,b)
for b in range(0,12):
  for n in range(0,14): add([0]*n,0,b)
print(len(cases),file=sys.stderr)
bad=0;tot=0;halts=0;tmo=0
BATCH=200
for i in range(0,len(cases),BATCH):
    ch=cases[i:i+BATCH]
    args=[EXE,M,'R','B','11','10','1','3','1','3','2','111001','50000000']+[','.join(map(str,ds))+';%d;%d'%(a,b) for ds,a,b in ch]
    out=subprocess.run(args,capture_output=True,text=True,env=env).stdout.strip().split('\n')
    assert len(out)==len(ch),(len(out),len(ch))
    for (ds,a,b),line in zip(ch,out):
        tot+=1
        ds0,a0,b0,res=parse(line)
        assert (tuple(ds0),a0,b0)==(ds,a,b),(line,ds,a,b)
        if isinstance(res,str):
            if 'HALT' in res: halts+=1
            else: tmo+=1
            bad+=1; print('NONRULE',line[:200]); continue
        p=pred(ds,a,b)
        if (res[0],res[1],res[2])!=p:
            bad+=1; print('MISMATCH',ds,a,b,'got',res[:3],'pred',p) if len(str(res))<300 else print('MISMATCH',ds,a,b,'long')
print('total',tot,'bad',bad,'halts',halts,'timeouts',tmo)
