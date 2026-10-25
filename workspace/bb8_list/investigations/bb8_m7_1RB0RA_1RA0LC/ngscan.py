import subprocess, sys, time
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m7_0RB0LC_ctl\ngcps2.exe'
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
LOW=0x40
pairs=[(a,b) for a in range(10,25,2) for b in range(10,25,2)]
pairs.sort(key=lambda p:(p[0]+p[1],p))
with open('ngscan.log','a') as f:
    for a,b in pairs:
        t=time.time()
        try:
            r=subprocess.run([EXE,M,str(a),str(b)],capture_output=True,text=True,timeout=90,creationflags=LOW)
            out=r.stdout.strip().split('\n')[0][:150]
        except subprocess.TimeoutExpired:
            out='TIMEOUT90'
        f.write('%d %d %.0fs %s\n'%(a,b,time.time()-t,out)); f.flush()
