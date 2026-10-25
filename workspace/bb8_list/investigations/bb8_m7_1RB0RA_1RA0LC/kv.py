import sys, subprocess
from tokv import *
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
def view(bits):
    if not bits.endswith('111001'): return 'NOTAIL '+rl(tokview(bits))[:300]
    R=bits[:-6]; z=''
    if R.endswith('0'): z='0'; R=R[:-1]   # extra zero
    return rl(tokview(R))[:500]+' |'+z+'S'
if __name__=='__main__':
    word,N,f,l,step = sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
    out = subprocess.run(['./snap.exe',M,word,'B',N,str(f),str(l)],capture_output=True,text=True).stdout
    k=0
    for line in out.splitlines():
        p=line.split()
        if len(p)==2 and p[0].isdigit():
            k+=1
            if (k-1)%step==0: print(p[0], view(p[1]))
        else: print(line[:200])
