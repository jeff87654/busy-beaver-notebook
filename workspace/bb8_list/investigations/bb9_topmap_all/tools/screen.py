import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""screen.py LIST OUTTSV RUNDIR NPAR WALL [pkf8 args]: W3 screen.  LIST lines 'id machine ...'.  Resumable (skips ids in OUTTSV).
Per machine: outcome, jumps, ones, step, #tops, top shapes+K (views '<=5 prefix tokens 1*K', K >= 1000), max K seen.
Keeps the run file in RUNDIR only if jumps >= 3 and not a tiny halt; PIDs -> pids.txt (own PIDs only)."""
import subprocess, time, re, collections
LIST, OUT, RD, NPAR, WALL = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]); ARGS = sys.argv[6:]
KMIN = int(os.environ.get("KMIN", "1000"))
EXE = os.path.join(BASE, 'tools', 'pkf8.exe'); os.makedirs(RD, exist_ok=True)
if ARGS and ARGS[0] == '--exe': EXE = os.path.join(BASE, 'tools', ARGS[1]); ARGS = ARGS[2:]
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
def summ(txt):
    out = 'KILLED'; ones = ''; step = ''; nj = 0; tops = []; maxk = 0
    for l in txt.splitlines():
        if l.startswith('J') and '|' in l:
            nj += 1; v = l.split('|', 1)[1].strip(); mm = TOP.match(v)
            for x in re.findall(r'1\*(\d+)', v): maxk = max(maxk, int(x))
            if mm and int(mm.group(2)) >= KMIN and len(mm.group(1).split()) <= 5:
                tops.append(re.sub(r'\d{3,}', 'X', mm.group(1)).strip().replace(' ', '.') + ':' + mm.group(2))
        elif l.startswith('HALT'):
            out = 'HALT_' + l.split()[1]; mo = re.search(r'ones (\d+)', l); ones = mo.group(1) if mo else ''
            mo = re.search(r'step (\d+)', l); step = mo.group(1) if mo else ''
        elif l.startswith('STOP'): out = 'STOP_NEEDK' if 'NEEDK' in l else 'STOP'
        elif l.startswith('END'): out = 'END'
    return out, nj, ones, step, tops, maxk
done = set()
if os.path.exists(OUT): done = {l.split('\t')[0] for l in open(OUT)}
jobs = [l.split()[:2] for l in open(LIST) if l.strip() and l.split()[0] not in done]
pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); fo = open(OUT, 'a'); run = []
pidf.write('%d driver screen.py %s %s\n' % (os.getpid(), LIST, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
import tempfile
while jobs or run:
    while jobs and len(run) < NPAR:
        n, m = jobs.pop(0); path = os.path.join(RD, n + '.txt'); fh = open(path, 'w')
        p = subprocess.Popen([EXE, m] + ARGS, stdout=fh, stderr=subprocess.STDOUT, creationflags=0x40)
        pidf.write('%d pkf8 screen %s\n' % (p.pid, n)); pidf.flush()
        run.append((p, fh, path, time.time(), n, m))
    time.sleep(0.05)
    for r in list(run):
        if r[0].poll() is None and time.time() - r[3] > WALL:
            subprocess.call(['taskkill', '/PID', str(r[0].pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); r[0].wait()
        if r[0].poll() is not None:
            r[1].close(); run.remove(r); txt = open(r[2], errors='replace').read()
            out, nj, ones, step, tops, maxk = summ(txt)
            if nj < 3 and out.startswith('HALT'): os.remove(r[2])
            fo.write('\t'.join([r[4], r[5], out, str(nj), ones, step, str(len(tops)), str(maxk), ' '.join(tops[:30]), '%.1f' % (time.time() - r[3])]) + '\n'); fo.flush()
print('screen done', LIST, flush=True)
