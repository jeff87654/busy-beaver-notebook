import subprocess,sys
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m7_1RB0RA_1RG0LC\e0z.exe'
def tape(K,L): return '10'*2+'1'*3+'00'+'100'*K+'1'*L+'00'+'1'+'00'+'1'
K0,K1,L0,L1,N=map(int,sys.argv[1:6])
for K in range(K0,K1+1):
    row=[]
    for L in range(L0,L1+1):
        r=subprocess.run([EXE,M,tape(K,L),'B',str(N)],capture_output=True,text=True,creationflags=0x40)
        o=r.stdout.strip()
        row.append('H' if o.startswith('HALT') else ('E' if o.startswith('EDGE') else '.'))
    print(f'K={K:3d} ',''.join(row),flush=True)
