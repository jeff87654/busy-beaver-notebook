"""wtree.py LIST OUTTSV RUNDIR NPAR WALL [pkf8 args...]
World-follower screen with TNF-lazy branching.  LIST lines: 'id machine' (machine may contain 'zzz' = lazy slot).
Each machine is run with pkf8t (lazy slots passed as '---').  If it halts on a lazy slot, a leaf 'halt there' is written and
the slot is branched over the 32 actions (only if another halt can remain).  Resumable: ids already in OUTTSV are skipped
(branch children get ids parent.Xc.val).
OUT columns: id machine outcome jumps ones step ntops tops(K list of '<=5-prefix 1*K' views, K>=KMIN) zeros(skeleton) lastview
Run files are kept in RUNDIR only for non-trivial runs (jumps >= 3)."""
import subprocess, sys, os, time, re, collections
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST, OUT, RD, NPAR, WALL = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]); ARGS = sys.argv[6:]
EXE = os.path.join(BASE, 'tools', os.environ.get('WEXE', 'pkf8t.exe'))
KMIN = int(os.environ.get('KMIN', '200'))
os.makedirs(RD, exist_ok=True)
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
NS = 8
VALS = ['%d%s%s' % (w, d, chr(65 + s)) for w in (0, 1) for d in 'LR' for s in range(NS)]

def slots(m): return [m[7 * q + 3 * b: 7 * q + 3 * b + 3] for q in range(len(m) // 7 + 1) for b in (0, 1)]
def setslot(m, idx, v):
    q, b = divmod(idx, 2); p = 7 * q + 3 * b; return m[:p] + v + m[p + 3:]

def summ(txt):
    out = 'KILLED'; ones = ''; step = ''; nj = 0; tops = []; zeros = ''; last = ''; hs = ''
    for l in txt.splitlines():
        if l.startswith('J') and '|' in l:
            nj += 1; v = l.split('|', 1)[1].strip(); last = v[:160]; mm = TOP.match(v)
            if mm and int(mm.group(2)) >= KMIN and len(mm.group(1).split()) <= 5:
                tops.append(int(mm.group(2)))
        elif l.startswith('HALT'):
            hs = l.split()[1]; out = 'HALT_' + hs; mo = re.search(r'ones (\d+)', l); ones = mo.group(1) if mo else ''
            mo = re.search(r'step (\d+)', l); step = mo.group(1) if mo else ''
        elif l.startswith('STOP'): out = 'STOP_' + (l.split()[1] if len(l.split()) > 1 else '')
        elif l.startswith('END'): out = 'END'
        elif l.startswith('zeros:'):
            zs = l.split()[1:]; comp = []
            for z in zs:
                if comp and comp[-1][0] == z: comp[-1][1] += 1
                else: comp.append([z, 1])
            zeros = ' '.join(z if c == 1 else '%sx%d' % (z, c) for z, c in comp)
            if len(zeros) > 300: zeros = zeros[:120] + ' ... ' + zeros[-150:]
    T = []
    for k in tops:
        if not T or T[-1] != k: T.append(k)
    return out, hs, nj, ones, step, T, zeros, last

done = set(); jobs = collections.deque()
for l in open(LIST):
    f = l.split()
    if len(f) >= 2 and not l.startswith('#'): jobs.append((f[0], f[1]))
if os.path.exists(OUT):
    for l in open(OUT):
        f = l.rstrip('\n').split('\t'); done.add(f[0])
        if '@lazy' in f[2]:   # regenerate the branch children of a finished lazy-halt row
            hs = f[2].split('_')[1].split('@')[0]; idx = 2 * (ord(hs[0]) - 65) + int(hs[1]); sl = slots(f[1])
            if any(x in ('zzz', '---') for i, x in enumerate(sl) if i != idx):
                for v in VALS: jobs.append((f[0] + '.' + hs + v, setslot(f[1], idx, v)))
pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); fo = open(OUT, 'a'); run = []
pidf.write('%d driver wtree.py %s %s\n' % (os.getpid(), LIST, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
while jobs or run:
    while jobs and len(run) < NPAR:
        n, m = jobs.popleft()
        if n in done:
            continue
        path = os.path.join(RD, n + '.txt'); fh = open(path, 'w')
        p = subprocess.Popen([EXE, m.replace('zzz', '---')] + ARGS, stdout=fh, stderr=subprocess.STDOUT, creationflags=0x40 | 0x08000000)
        pidf.write('%d pkf8t %s\n' % (p.pid, n)); pidf.flush()
        run.append((p, fh, path, time.time(), n, m))
    time.sleep(0.03)
    for r in list(run):
        p, fh, path, t0, n, m = r
        if p.poll() is None and time.time() - t0 > WALL:
            subprocess.call(['taskkill', '/PID', str(p.pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); p.wait()
        if p.poll() is not None:
            fh.close(); run.remove(r); txt = open(path, errors='replace').read()
            out, hs, nj, ones, step, T, zeros, last = summ(txt)
            if out == 'KILLED': out = 'WALL'
            sl = slots(m)
            branched = False
            if hs and len(hs) == 2:
                idx = 2 * (ord(hs[0]) - 65) + int(hs[1])
                if idx < len(sl) and sl[idx] == 'zzz':
                    out += '@lazy'
                    other = any(s in ('zzz', '---') for i, s in enumerate(sl) if i != idx)
                    if other:
                        for v in VALS: jobs.appendleft((n + '.' + hs + v, setslot(m, idx, v)))
                        branched = True
            fo.write('\t'.join([n, m, out, str(nj), ones, step, str(len(T)), ','.join(map(str, T[:30])), zeros, last]) + '\n'); fo.flush()
            if nj < 3 and not out.startswith(('STOP', 'END', 'WALL')): os.remove(path)
print('done')
