"""screen_f3.py LISTFILE WORLDNAME "pkf args" [NPAR] [WALLSEC]
Runs tools/pkf8.exe on every machine of LISTFILE (lines "name machine") from the blank tape, NPAR at a time, each limited to
WALLSEC wall seconds (killed by its own PID only).  Output runs/<world>/<name>.txt, summary runs/<world>/summary.tsv:
  name  outcome  jumps  zeros(cleared depths, compressed)  ones  #I0-segments  last view
PIDs are appended to pids.txt (real Windows PIDs from Popen; pkf8 sets Idle priority itself)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import idle
import subprocess, sys, os, time, re
LIST, WNAME, WARGS = sys.argv[1], sys.argv[2], sys.argv[3]
NPAR = int(sys.argv[4]) if len(sys.argv) > 4 else 2
WALL = float(sys.argv[5]) if len(sys.argv) > 5 else 900
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
odir = os.path.join(BASE, 'runs', WNAME); os.makedirs(odir, exist_ok=True)
jobs = [ln.split()[:3] for ln in open(LIST) if ln.strip() and not ln.startswith('#')]
DONE = set(l.split('	')[0] for l in open(os.path.join(odir, 'summary.tsv'))) if os.path.exists(os.path.join(odir, 'summary.tsv')) else set()
jobs = [j for j in jobs if j[0] not in DONE]

def summarize(name, m, path, killed):
    out = 'KILLED' if killed else 'RUNNING'; ones = ''; nj = 0; zeros = ''; last = ''; ni0 = 0
    for l in open(path, errors='replace'):
        if l.startswith('J'):
            nj += 1
            if 'I0' in l.split('used=')[-1].split('|')[0]: ni0 += 1
            last = l.split('|', 1)[1].strip()[:120] if '|' in l else ''
        elif l.startswith('HALT'):
            out = 'HALT ' + l.split()[1]; mo = re.search(r'ones (\d+)', l); ones = mo.group(1) if mo else ''
        elif l.startswith('STOP'): out = 'STOP ' + l.split()[-1]
        elif l.startswith('END'): out = 'END'
        elif l.startswith('RCAP'): out = 'RCAP'
        elif l.startswith('zeros:'): zeros = l[6:].strip()
        elif l.startswith('  tape:') and out.startswith(('HALT', 'STOP')): last = l.split(':', 1)[1].strip()[:120]
    zs = zeros.split(); comp = []
    for k in zs:
        if comp and comp[-1][0] == k: comp[-1][1] += 1
        else: comp.append([k, 1])
    zc = ' '.join(k if c == 1 else '%sx%d' % (k, c) for k, c in comp)
    if len(zc) > 120: zc = zc[:50] + ' ... ' + zc[-65:]
    return '\t'.join([name, out, str(nj), zc, ones, str(ni0), last, m])

running = []; i = 0
open(os.path.join(BASE, 'pids.txt'), 'a').write('%d driver screen.py %s %s' % (os.getpid(), WNAME, time.strftime('%m-%d %H:%M:%S')) + chr(10))
summ = open(os.path.join(odir, 'summary.tsv'), 'a'); pidf = open(os.path.join(BASE, 'pids.txt'), 'a')
while i < len(jobs) or running:
    while i < len(jobs) and len(running) < NPAR:
        name, m = jobs[i][:2]; qa = ['--Q', jobs[i][2]] if len(jobs[i]) > 2 and jobs[i][2] != 'None' else []; i += 1
        path = os.path.join(odir, name + '.txt'); fo = open(path, 'w')
        p = subprocess.Popen([EXE, m] + WARGS.split() + qa, stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
        pidf.write('%d screen %s %s %s\n' % (p.pid, WNAME, name, time.strftime('%H:%M:%S'))); pidf.flush()
        running.append([p, fo, name, m, path, time.time()])
    time.sleep(2)
    for r in running[:]:
        killed = False
        if r[0].poll() is None and time.time() - r[5] > WALL:
            subprocess.call(['taskkill', '/PID', str(r[0].pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            killed = True; time.sleep(1)
        if r[0].poll() is not None or killed:
            r[1].close(); running.remove(r)
            summ.write(summarize(r[2], r[3], r[4], killed) + '\n'); summ.flush()
print('done', len(jobs))
