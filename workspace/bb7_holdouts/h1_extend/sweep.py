# sweep.py JOBFILE : run xs.exe jobs (one per line: OUT MACHINE K BUDGET TEMPLATE PNAME LO HI) on 2 Idle workers; log pids
import subprocess, sys, os, threading, queue, shlex
D = os.path.dirname(os.path.abspath(__file__)); XS = os.path.join(D, "src", os.environ.get("XSEXE", "xs.exe"))
q = queue.Queue(); lock = threading.Lock()
for l in open(sys.argv[1]):
    if l.strip() and not l.startswith('#'): q.put(shlex.split(l))
def w():
    while True:
        try: j = q.get_nowait()
        except queue.Empty: return
        out = os.path.join(D, j[0]); env = dict(os.environ); 
        for kv in j[8:]: k, v = kv.split('='); env[k] = v
        with open(out, 'w') as f:
            p = subprocess.Popen([XS] + j[1:8], stdout=f, creationflags=0x40, env=env)
            with lock: open(os.path.join(D, 'pids.txt'), 'a').write(f"{p.pid} xs.exe {j[0]}\n")
            p.wait()
ts = [threading.Thread(target=w) for _ in range(int(os.environ.get('NW', '2')))]
[t.start() for t in ts]; [t.join() for t in ts]
