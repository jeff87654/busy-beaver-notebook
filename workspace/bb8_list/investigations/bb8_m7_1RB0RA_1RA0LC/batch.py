import subprocess, itertools
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
def run(cfgs, tail='0111001', P=1, N=2000000):
    """cfgs: list of (tokens, r). returns list of (tokens,r, result) where result = (step, toks, r) or string"""
    inp='\n'.join(' '.join(map(str,t))+' | '+str(r) for t,r in cfgs)+'\n'
    out=subprocess.run(['./gk6.exe',M,tail,str(P),str(N)],input=inp,capture_output=True,text=True).stdout.strip().split('\n')
    res=[]
    for (t,r),l in zip(cfgs,out):
        rhs=l.split(' => ')[1]
        if rhs[0].isdigit():
            a,b=rhs.split(':'); toks,rr=b.split('|')
            res.append((t,r,(int(a),[int(x) for x in toks.split()],int(rr))))
        else: res.append((t,r,rhs))
    return res
