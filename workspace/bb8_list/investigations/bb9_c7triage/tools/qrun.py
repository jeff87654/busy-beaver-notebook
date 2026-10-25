import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import idle
"""qrun.py NPAR: dynamic job runner.  Jobs are lines of prio.txt (served first) then queue.txt:
     id <TAB> outfile <TAB> wallsec <TAB> machine <TAB> pkf8 args
A job is skipped if its id is in qdone.txt.  Runs tools/pkf8.exe at IDLE priority, kills by own PID after wallsec
(the output then lacks HALT/STOP/END = KILLED).  Stops when the file qstop exists and nothing runs.
PIDs -> pids.txt."""
import subprocess, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
NPAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2
P = lambda f: os.path.join(BASE, f)
open(P('pids.txt'), 'a').write('%d driver qrun.py %s\n' % (os.getpid(), time.strftime('%m-%d %H:%M:%S')))
def done_ids():
    return set(l.split()[0] for l in open(P('qdone.txt'))) if os.path.exists(P('qdone.txt')) else set()
def jobs():
    out = []
    for f in ('prio.txt', 'queue.txt'):
        if os.path.exists(P(f)):
            for l in open(P(f)):
                p = l.rstrip('\n').split('\t')
                if len(p) >= 5: out.append(p)
    return out
running = {}
while True:
    dn = done_ids()
    if len(running) < NPAR:
        for j in jobs():
            if len(running) >= NPAR: break
            if j[0] in dn or j[0] in running: continue
            outf = P(j[1]); os.makedirs(os.path.dirname(outf), exist_ok=True)
            fo = open(outf, 'w')
            pr = subprocess.Popen([EXE, j[3]] + j[4].split(), stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
            open(P('pids.txt'), 'a').write('%d qrun %s %s\n' % (pr.pid, j[0], time.strftime('%m-%d %H:%M:%S')))
            running[j[0]] = [pr, fo, time.time(), float(j[2])]
    time.sleep(2)
    for jid, r in list(running.items()):
        if r[0].poll() is None and time.time() - r[2] > r[3]:
            subprocess.call(['taskkill', '/PID', str(r[0].pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        if r[0].poll() is not None:
            r[1].close(); del running[jid]
            open(P('qdone.txt'), 'a').write('%s %s %.0f\n' % (jid, time.strftime('%m-%d %H:%M:%S'), time.time() - r[2]))
    if not running and os.path.exists(P('qstop')):
        dn = done_ids()
        if all(j[0] in dn for j in jobs()): break
print('qrun exit')
