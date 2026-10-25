from batch import *
from seqx import rl
import subprocess, sys
M2='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
def events(toks,r,N,P=1,tail='111001'):
    w=('11' if P else '')+''.join('10'*m+'1' for m in toks)+'10'*r+tail
    out=subprocess.run(['./gk5.exe',M2,w,'B',str(N),'100000',tail,str(P)],capture_output=True,text=True).stdout.strip().split('\n')
    evs=[];prev=(toks,r)
    for l in out:
        if l.startswith('step'):
            st=int(l.split()[1]); body=l[l.index('[')+1:l.index(']')]
            t=[int(x) for x in body.split(',')] if body else []; rr=int(l.split('r=')[1])
            pt,pr=prev
            if len(pt)==len(t) and pt[:-1]==t[:-1] and pt[-1]-3==t[-1] and rr==2*pr+4: prev=(t,rr); continue
            evs.append((st,rl(t),rr)); prev=(t,rr)
        else: evs.append(l)
    return evs
if __name__=='__main__':
    toks=eval(sys.argv[1]); r=int(sys.argv[2]); N=int(sys.argv[3])
    for e in events(toks,r,N): print(e)
