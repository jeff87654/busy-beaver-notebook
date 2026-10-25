import idle, sys
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters')
from lit import parse
def seq(m,N):
    T=parse(m); tape=bytearray(4*N+10); p=2*N+5; q=0; ones=0; out=[]
    for st in range(N):
        c=tape[p]; tr=T[(q,c)]
        if tr is None: break
        w,d,nq=tr; ones+=w-c; tape[p]=w; p+=d; q=nq; out.append(ones)
    return out
rows=[l.split()[0] for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\pool_f_nofit.txt') if l.startswith('1RB')]
N=int(sys.argv[1]); W=60000
S=[seq(m,N) for m in rows]
grp=[-1]*len(rows); g=0; info={}
for i in range(len(rows)):
    if grp[i]>=0: continue
    grp[i]=g; info[i]=(g,0)
    for j in range(i+1,len(rows)):
        if grp[j]>=0: continue
        for k in range(0,60):
            if S[j][k:k+W]==S[i][:W] or S[i][k:k+W]==S[j][:W]:
                grp[j]=g; info[j]=(g,k if S[j][k:k+W]==S[i][:W] else -k); break
    g+=1
for gi in range(g):
    mem=[i for i in range(len(rows)) if grp[i]==gi]
    print('G%d'%gi, len(mem))
    for i in mem: print('   ',rows[i],'shift',info[i][1])
