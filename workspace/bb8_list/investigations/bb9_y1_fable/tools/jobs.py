"""jobs.py JOBFILE OUTDIR [NPAR] [WALLSEC] : each JOBFILE line "name | machine | extra args"; runs tools/pkf8.exe machine args
NPAR at a time (default 2), each killed by PID after WALLSEC (default 900). Output runs/OUTDIR/name.txt, PIDs -> pids.txt."""
import subprocess, sys, os, time
JOBF, OUT = sys.argv[1], sys.argv[2]; NPAR = int(sys.argv[3]) if len(sys.argv) > 3 else 2
WALL = float(sys.argv[4]) if len(sys.argv) > 4 else 900
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
odir = os.path.join(BASE, 'runs', OUT); os.makedirs(odir, exist_ok=True)
jobs = [[x.strip() for x in ln.split('|')] for ln in open(JOBF) if ln.strip() and not ln.startswith('#')]
running = []; i = 0; pidf = open(os.path.join(BASE, 'pids.txt'), 'a')
while i < len(jobs) or running:
    while i < len(jobs) and len(running) < NPAR:
        name, m, args = jobs[i]; i += 1
        fo = open(os.path.join(odir, name + '.txt'), 'w')
        p = subprocess.Popen([EXE, m] + args.split(), stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
        pidf.write('%d jobs %s %s %s\n' % (p.pid, OUT, name, time.strftime('%H:%M:%S'))); pidf.flush()
        running.append([p, fo, name, time.time()])
    time.sleep(2)
    for r in running[:]:
        if r[0].poll() is None and time.time() - r[3] > WALL:
            subprocess.call(['taskkill', '/PID', str(r[0].pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            r[1].write('\nKILLED wall %ds\n' % WALL); time.sleep(1)
        if r[0].poll() is not None: r[1].close(); running.remove(r)
print('done', len(jobs))
