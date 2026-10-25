import subprocess
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
w=open('first_word.txt').read()
out=subprocess.run(['./gk5.exe',M,w,'B','4000000000','100000','111001','1'],capture_output=True,text=True).stdout.strip().split('\n')
cfgs=[]
for l in out:
    if l.startswith('step'):
        body=l[l.index('[')+1:l.index(']')]
        cfgs.append(([int(x) for x in body.split(',')],int(l.split('r=')[1])))
    else: print(l)
print(len(cfgs),'K snapshots')
def pred(toks,r):
    a=toks[-1]
    if a>=4: return toks[:-1]+[a-3],2*r+4
    if a==1:
        j=len(toks)-2
        while j>=0 and toks[j]==1: j-=1
        if j<0: return 'USED'
        t=toks[j]; new=list(toks); new[j]=t-3; new[j+1]=2*r+3
        return new,2
    return 'A?'
# the first snapshot may be the initial config's successor; check consecutive pairs
ok=0;bad=0
for i in range(len(cfgs)-1):
    p=pred(*cfgs[i])
    if p==cfgs[i+1]: ok+=1
    else:
        bad+=1; print('MISMATCH at',i,cfgs[i][0][:14],cfgs[i][1],'->',cfgs[i+1][0][:14],cfgs[i+1][1],'pred',p if isinstance(p,str) else (p[0][:14],p[1]))
print('ok',ok,'bad',bad)
