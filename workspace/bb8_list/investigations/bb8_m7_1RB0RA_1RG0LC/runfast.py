import subprocess,sys,time,os
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m7_1RB0RA_1RG0LC\ngfast.exe'
T=int(sys.argv[1]); env=dict(os.environ,NG_CAP=os.environ.get('NG_CAP','60000000'))
for a in sys.argv[2:]:
    nl,nr=map(int,a.split('/'))
    t=time.time()
    try:
        r=subprocess.run([EXE,M,str(nl),str(nr)],capture_output=True,text=True,timeout=T,creationflags=0x40,env=env)
        print(a,r.stdout.strip()[:150],f'{time.time()-t:.0f}s',flush=True)
    except subprocess.TimeoutExpired:
        print(a,'TIMEOUT',T,flush=True)
