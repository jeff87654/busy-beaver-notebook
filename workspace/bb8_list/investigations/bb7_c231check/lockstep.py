import idle, sys, re
from predict import predict   # exact rule + step prediction
w=int(sys.argv[1]); fn=sys.argv[2]
def parse(line):
    t=line.split(); 
    if t[0]!='K': return None
    step=int(t[1]); runs=[tuple(map(int,x.split('^'))) for x in t[2:]]
    # drop trailing zero runs
    while runs and runs[-1][0]==0: runs.pop()
    s=''.join(str(b)*c for b,c in runs)
    m=re.fullmatch(r'100((?:11)*)00((?:(?:11)*00)*)1',s)
    if not m: return None
    a=len(m.group(1))//2; ds=[len(x)//2 for x in m.group(2).split('00')[:-1]]
    return step,a,ds
seq=[]
for line in open(fn):
    p=parse(line)
    if p: seq.append(p)
print('literal K-configs:',len(seq),'first',seq[0][0],seq[0][1],len(seq[0][2]))
ok=0
for (s0,a0,d0),(s1,a1,d1) in zip(seq,seq[1:]):
    p=predict(a0,d0,w)
    if p[0]=='K' and s1-s0==p[1] and (a1,d1)==p[2]: ok+=1
    else: print('MISMATCH at',s0,a0,d0[:5],'pred',p[:2],'got',s1-s0,a1,d1[:5]); break
print('consecutive pairs matching rule+exact steps:',ok,'of',len(seq)-1)
s,a,d=seq[-1]; print('last literal K:',s,'a=',a,'ds[:4]=',d[:4],'n=',len(d))
