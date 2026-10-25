"""runevo.py OUT N K INFILE: src/evo.exe at Idle priority, logs PID"""
import idle, subprocess, sys, os, time
out, N, K, inf = sys.argv[1:5]
with open(inf) as fi, open(out, 'w') as fo:
    p = subprocess.Popen([os.path.abspath('src/evo.exe'), N, K], stdin=fi, stdout=fo, creationflags=0x40)
    with open('pids.txt', 'a') as fp: fp.write(f"{time.strftime('%F %H:%M')} {p.pid} evo {N} {K} {inf} -> {out}\n")
    p.wait()
