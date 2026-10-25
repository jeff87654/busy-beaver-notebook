import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""qrun.py LIST ODIR NPAR WALL [pkf8 args...]: run pkf8 on every 'name machine' line of LIST (skip names whose ODIR/<name>.txt
has a final HALT/STOP/END line), output ODIR/<name>.txt, at most NPAR at a time, kill (own PID) after WALL s.  PIDs -> pids.txt."""
import subprocess, time
LIST, ODIR, NPAR, WALL = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]); ARGS = sys.argv[5:]
EXE = os.path.join(BASE, 'tools', 'pkf8.exe'); os.makedirs(ODIR, exist_ok=True)
def fin(f):
    if not os.path.exists(f): return False
    return any(l.startswith(('HALT', 'STOP', 'END', 'KILLED')) for l in open(f, errors='replace'))
jobs = [l.split()[:2] for l in open(LIST) if l.strip()]
jobs = [j for j in jobs if not fin(os.path.join(ODIR, j[0] + '.txt'))]
pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); run = []
pidf.write('%d driver qrun.py %s %s\n' % (os.getpid(), LIST, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
while jobs or run:
    while jobs and len(run) < NPAR:
        n, m = jobs.pop(0); path = os.path.join(ODIR, n + '.txt'); fo = open(path, 'w')
        p = subprocess.Popen([EXE, m] + ARGS, stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
        pidf.write('%d pkf8 qrun %s %s\n' % (p.pid, n, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
        run.append((p, fo, path, time.time()))
    time.sleep(0.5)
    for r in list(run):
        if r[0].poll() is None and time.time() - r[3] > WALL:
            subprocess.call(['taskkill', '/PID', str(r[0].pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); r[0].wait()
            r[1].write('KILLED wall\n')
        if r[0].poll() is not None: r[1].close(); run.remove(r)
print('qrun done', LIST, flush=True)
