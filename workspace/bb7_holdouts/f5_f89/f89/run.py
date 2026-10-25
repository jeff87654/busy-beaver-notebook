# run.py "d1 d2 ..." [maxsteps] [nevents] : build K tape (prefix 1, digits (01)^d 1), run kl, print p1 events
import sys,subprocess,os
from ev import parse, rl
M='1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE'
KL=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\f5_f89\f89\kl2.exe'
def tape(digs,pre='00'):
    return 'D0'+pre+''.join('1'+'01'*d for d in digs)
def expand(s):
    out=[]
    for t in s.split():
        if '^' in t: v,n=t.split('^'); out+= [int(v)]*int(n)
        else: out.append(int(t))
    return out
def events(digs,maxs=10**7,nev=20,allp=False,m=M):
    env=dict(os.environ,U='01',NEV=str(nev))
    p=subprocess.run([KL,m,str(maxs),'D','L','a',tape(digs)],capture_output=True,text=True,env=env)
    res=[]
    for line in p.stdout.splitlines():
        q=line.split()
        if q[0]=='HALT' or q[0]=='LIMIT': res.append(line); break
        pre,d=parse(q[1:])
        if pre!=1 and not allp: continue
        res.append((int(q[0]),pre,d))
        if len(res)>=nev: break
    return res
if __name__=='__main__':
    d=expand(sys.argv[1]); ms=int(sys.argv[2]) if len(sys.argv)>2 else 10**7; ne=int(sys.argv[3]) if len(sys.argv)>3 else 20
    for r in events(d,ms,ne,allp=len(sys.argv)>4):
        print(r if isinstance(r,str) else '%d %d | %s'%(r[0],r[1],rl(r[2])))
