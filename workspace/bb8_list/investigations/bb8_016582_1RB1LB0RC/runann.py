import subprocess,sys,time
M="1RB1LB_0RC---_1RD1RG_0LE0RH_1LF1LE_0RD0RA_1RB0LE_1RC0LD"
if sys.argv[1]=='mirror': M=M.translate(str.maketrans('LR','RL'))
exe='../bb8_m7_1RB0RA_1RG0LC/opus/ngann.exe'
pairs=sys.argv[2].split(','); T=int(sys.argv[3]); extra=sys.argv[4:]
for pr in pairs:
    a,b=pr.split('/')
    t0=time.time()
    try:
        r=subprocess.run([exe,M,a,b]+extra,capture_output=True,text=True,timeout=T,creationflags=0x40)
        out=(r.stdout+r.stderr).strip().splitlines()
        print(pr,extra,round(time.time()-t0),out[-2:] if out else '',flush=True)
        if r.stdout.startswith('NONHALT'): break
    except subprocess.TimeoutExpired:
        print(pr,'TIMEOUT',flush=True)
