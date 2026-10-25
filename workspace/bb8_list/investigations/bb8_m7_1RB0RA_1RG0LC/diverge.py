import subprocess,sys,re
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m7_0RB0LC_opus\tsnap.exe'
M1='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
M0='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE'
def m3(K,n): return '10'*2+'1'*3+'00'+'100'*K+'1'*(3*n+7)+'00'+'1'+'00'+'1'
def run(M,w,N):
    r=subprocess.run([EXE,M,w,str(len(w)),'B',str(N),'1.0','1000000000'],capture_output=True,text=True,creationflags=0x40)
    out=[]
    for ln in r.stdout.split('\n'):
        m=re.match(r'\d+ \[(\d+)\] (.*)',ln)
        if m: out.append(m.group(2).strip())
    return out
K0,K1,n0,n1,N=map(int,sys.argv[1:6])
for n in range(n0,n1+1):
    for K in range(K0,K1+1):
        w=m3(K,n); a=run(M1,w,N); b=run(M0,w,N)
        d=None
        for i in range(min(len(a),len(b))):
            if a[i]!=b[i]: d=i;break
        if d is None: print(f'K={K} n={n}: same through {min(len(a),len(b))} snapshots',flush=True)
        else: print(f'K={K} n={n}: diverge at snapshot {d}\n   common: {a[d-1][:150]}\n   ours  : {a[d][:150]}\n   theirs: {b[d][:150]}',flush=True)
