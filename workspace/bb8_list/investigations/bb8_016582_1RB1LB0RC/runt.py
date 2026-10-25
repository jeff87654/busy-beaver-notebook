import subprocess,sys,time
M="1RB1LB_0RC---_1RD1RG_0LE0RH_1LF1LE_0RD0RA_1RB0LE_1RC0LD"
exe='../bb8_m7_0RB0LC_ctl/tctl.exe'
for spec in sys.argv[2:]:
    args=spec.split(',')
    t0=time.time()
    try:
        r=subprocess.run([exe,M]+args,capture_output=True,text=True,timeout=int(sys.argv[1]),creationflags=0x40)
        out=(r.stdout+r.stderr).strip().splitlines()
        print(spec,round(time.time()-t0),out[-3:] if out else '',flush=True)
    except subprocess.TimeoutExpired:
        print(spec,'TIMEOUT',flush=True)
