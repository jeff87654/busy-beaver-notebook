# batch.py LOG T PAR EXE "params" ... : run EXE MACHINE params at Idle priority, PAR at a time, timeout T s each; append results to LOG
import subprocess,sys,time,os
M=os.environ.get('MACH','1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE')
log=sys.argv[1]; T=int(sys.argv[2]); PAR=int(sys.argv[3]); EXE=sys.argv[4]; jobs=sys.argv[5:]
env=dict(os.environ); env.setdefault('TC_CAP','150000000')
running=[]
def flush(p,a,t0,f):
    out=open(f).read().strip().splitlines() if os.path.exists(f) else []
    first=' | '.join(out[:3])[:600]
    with open(log,'a') as L: L.write(f'{a} :: {first} :: {time.time()-t0:.0f}s rc={p.returncode}\n')
    os.remove(f)
i=0
while i<len(jobs) or running:
    while i<len(jobs) and len(running)<PAR:
        a=jobs[i]; i+=1
        f=f'{log}.{i}.tmp'
        p=subprocess.Popen([EXE,M,*a.split()],stdout=open(f,'w'),stderr=subprocess.DEVNULL,creationflags=0x40,env=env)
        running.append((p,a,time.time(),f))
    time.sleep(1)
    for r in running[:]:
        p,a,t0,f=r
        if p.poll() is not None: flush(p,a,t0,f); running.remove(r)
        elif time.time()-t0>T: p.kill(); p.wait(); flush(p,a+' TIMEOUT',t0,f); running.remove(r)
with open(log,'a') as L: L.write('BATCH DONE\n')
