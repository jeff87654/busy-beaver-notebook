import subprocess, sys, random
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
def D(m): return '10'*m+'1'
def wordx(toks,r,P=True,tail='0111001'):
    return ('11' if P else '')+''.join(D(m) for m in toks)+'10'*r+tail
def litx(toks,r,P=True,N=30000000,tail='0111001',maxprint=1,skip=0):
    w=wordx(toks,r,P,tail)
    out=subprocess.run(['./gk5.exe',M,w,'B',str(N),str(maxprint),tail,'1' if P else '0',str(skip)],capture_output=True,text=True).stdout.strip().split('\n')
    res=[]
    for l in out:
        if l.startswith('step'):
            st=int(l.split()[1]); body=l[l.index('[')+1:l.index(']')]
            toks2=[int(x) for x in body.split(',')] if body else []
            r2=int(l.split('r=')[1].split()[0])
            res.append((st,toks2,r2))
        elif l.startswith('HALT') or l.startswith('EDGE'): res.append(l)
    return res
if __name__=='__main__':
    toks=eval(sys.argv[1]); r=int(sys.argv[2]); P=sys.argv[3]=='1'
    for x in litx(toks,r,P,maxprint=int(sys.argv[4])): print(x)
