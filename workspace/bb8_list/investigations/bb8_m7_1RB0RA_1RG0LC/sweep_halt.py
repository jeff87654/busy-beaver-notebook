import subprocess,sys,os
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m7_1RB0RA_1RG0LC\e0z.exe'
def m3(K,n): return '10'*2+'1'*3+'00'+'100'*K+'1'*(3*n+7)+'00'+'1'+'00'+'1'
K0,K1,n0,n1,N=map(int,sys.argv[1:6])
for K in range(K0,K1+1):
    for n in range(n0,n1+1):
        r=subprocess.run([EXE,M,m3(K,n),'B',str(N)],capture_output=True,text=True,creationflags=0x40)
        o=r.stdout.strip()
        flag='' if o.startswith('ok') else '  <<<<<<<<'
        print(f'K={K} n={n} {o}{flag}',flush=True)
