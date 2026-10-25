"""run.py OUT N INFILE : runs src/g6.exe at Idle priority, logs PID to pids.txt"""
import idle, subprocess, sys, os, time
out, N, inf = sys.argv[1], sys.argv[2], sys.argv[3]
exe = os.path.abspath('src/g6.exe')
with open(inf) as fi, open(out, 'w') as fo:
    p = subprocess.Popen([exe, N, '40'], stdin=fi, stdout=fo, creationflags=0x40)
    with open('pids.txt', 'a') as fp: fp.write(f"{time.strftime('%F %H:%M')} {p.pid} g6 {N} {inf} -> {out}\n")
    p.wait()
