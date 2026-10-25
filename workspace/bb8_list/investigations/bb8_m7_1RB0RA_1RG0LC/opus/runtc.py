# runtc.py T MACHINE|ours|theirs  kL/kR/ML/MR ... : run tcps.exe at Idle priority with a timeout per run
import subprocess,sys,time,os
MS={'ours':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE',
    'theirs':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE',
    'lg':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LG0LC_1RG1LD_0RH0RF_---0RE'}
EXE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tcps.exe')
T=int(sys.argv[1]); M=MS.get(sys.argv[2],sys.argv[2])
env=dict(os.environ); env.setdefault('TC_CAP','80000000')
for a in sys.argv[3:]:
    p=a.split('/')
    t=time.time()
    try:
        r=subprocess.run([EXE,M,*p],capture_output=True,text=True,timeout=T,creationflags=0x40,env=env)
        print(a,r.stdout.strip()[:2000],f'{time.time()-t:.0f}s',flush=True)
    except subprocess.TimeoutExpired:
        print(a,'TIMEOUT',T,flush=True)
