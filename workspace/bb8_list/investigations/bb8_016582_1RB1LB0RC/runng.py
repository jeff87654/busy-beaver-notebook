import subprocess,sys,time
M="1RB1LB_0RC---_1RD1RG_0LE0RH_1LF1LE_0RD0RA_1RB0LE_1RC0LD"
exe=sys.argv[1]; pairs=sys.argv[2].split(','); T=int(sys.argv[3]); extra=sys.argv[4:]
for pr in pairs:
    a,b=pr.split('/')
    t0=time.time()
    try:
        r=subprocess.run([exe,M,a,b]+extra,capture_output=True,text=True,timeout=T,creationflags=0x40)
        out=(r.stdout+r.stderr).strip().splitlines()
        print(pr,round(time.time()-t0),out[-3:] if out else '',flush=True)
        if r.stdout.startswith('NONHALT'): break
    except subprocess.TimeoutExpired:
        print(pr,'TIMEOUT',flush=True)
