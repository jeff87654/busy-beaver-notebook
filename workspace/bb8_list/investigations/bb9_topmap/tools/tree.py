import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""tree.py TAG E0 H0 [H1] [NPAR] [JUMPS] [MAXT] [WALL]: TNF-style tree over the I row of
   1RB0RA_1LC1LF_1RD0LB_1RA1LE_<E0>0LC_1RG1LD_0RG0RF_<H0><H1>_<I0><I1>   (M8 engine; default H1 = ---)
Root I = ------; a run that halts on an undefined I slot is expanded over the 36 values of that slot.
World W3: --B 366 --cls 366 --mod 3600 --cnt (residue-faithful mod 3600 and 125).  Idle priority; PIDs -> pids.txt.
Output: runs/A_<TAG>/<id>.txt and runs/A_<TAG>/tree.tsv (id machine outcome jumps ones zeros)."""
import subprocess, time, re, collections
TAG, E0, H0 = sys.argv[1], sys.argv[2], sys.argv[3]
H1 = sys.argv[4] if len(sys.argv) > 4 else '---'
NPAR = int(sys.argv[5]) if len(sys.argv) > 5 else 2
JUMPS = sys.argv[6] if len(sys.argv) > 6 else '30'
MAXT = sys.argv[7] if len(sys.argv) > 7 else '2e9'
WALL = float(sys.argv[8]) if len(sys.argv) > 8 else 60
EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
ODIR = os.path.join(BASE, 'runs', 'A_' + TAG); os.makedirs(ODIR, exist_ok=True)
TSV = os.path.join(ODIR, 'tree.tsv')
VALS = [w + d + s for w in '01' for d in 'LR' for s in 'ABCDEFGHI']
def mach(i0, i1): return '1RB0RA_1LC1LF_1RD0LB_1RA1LE_%s0LC_1RG1LD_0RG0RF_%s%s_%s%s' % (E0, H0, H1, i0, i1)
done = {}
if os.path.exists(TSV):
    for l in open(TSV):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 3: done[p[1]] = p[2]
def summarize(path):
    out = 'KILLED'; ones = ''; zeros = ''; nj = 0
    for l in open(path, errors='replace'):
        if l.startswith('J'): nj += 1
        elif l.startswith('HALT'): out = 'HALT ' + l.split()[1]; mo = re.search(r'ones (\d+)', l); ones = mo.group(1) if mo else ''
        elif l.startswith('STOP'): out = 'STOP'
        elif l.startswith('END'): out = 'END'
        elif l.startswith('zeros:'): zeros = l[6:].strip()
    return out, nj, ones, zeros
pend = collections.deque([('------'[:3], '------'[3:])])
running = []; pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); tsv = open(TSV, 'a')
pidf.write('%d driver tree.py %s %s\n' % (os.getpid(), TAG, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
def expand(i0, i1, out):
    if out == 'HALT I0' and i0 == '---': pend.extend((v, i1) for v in VALS)
    elif out == 'HALT I1' and i1 == '---': pend.extend((i0, v) for v in VALS)
while pend or running:
    while pend and len(running) < NPAR:
        i0, i1 = pend.popleft(); m = mach(i0, i1)
        if m in done: expand(i0, i1, done[m]); continue
        mid = (i0 + i1).replace('-', 'x')
        path = os.path.join(ODIR, mid + '.txt'); fo = open(path, 'w')
        p = subprocess.Popen([EXE, m, '--B', '366', '--cls', '366', '--mod', '3600', '--cnt', '--jumps', JUMPS, '--maxs', '1e9', '--maxt', MAXT, '--view', '300'],
                             stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
        pidf.write('%d pkf8 %s %s %s\n' % (p.pid, TAG, mid, time.strftime('%H:%M:%S'))); pidf.flush()
        running.append([p, fo, i0, i1, m, mid, path, time.time()])
    time.sleep(0.2)
    for r in list(running):
        p = r[0]
        if p.poll() is None and time.time() - r[7] > WALL:
            subprocess.call(['taskkill', '/PID', str(p.pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); p.wait()
        if p.poll() is not None:
            r[1].close(); running.remove(r)
            out, nj, ones, zeros = summarize(r[6]); done[r[4]] = out
            tsv.write('\t'.join([r[5], r[4], out, str(nj), ones, zeros]) + '\n'); tsv.flush()
            expand(r[2], r[3], out)
print('tree done', TAG)
