# simc.py LEFT STATE SCANNED RIGHT N : literal run of a concrete config (left/right as tape strings left-to-right)
import sys
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
tm={}
for i,r in enumerate(M.split('_')):
    for c in range(2):
        t=r[3*c:3*c+3]; tm[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
def run(left,q,m,right,N,show=False):
    tape={}; 
    for i,c in enumerate(left): tape[i-len(left)]=int(c)
    tape[0]=int(m)
    for i,c in enumerate(right): tape[i+1]=int(c)
    p=0; q=ord(q)-65
    for n in range(N):
        t=tm[(q,tape.get(p,0))]
        if t is None: return ('HALT',n,tape,p)
        tape[p]=t[0]; p+=t[1]; q=t[2]
    return ('run',N,tape,p,q)
if __name__=='__main__':
    r=run(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]))
    tape=r[2]; lo=min(tape); hi=max(tape)
    print(r[0],r[1],''.join(str(tape.get(i,0)) for i in range(lo,hi+1)))
