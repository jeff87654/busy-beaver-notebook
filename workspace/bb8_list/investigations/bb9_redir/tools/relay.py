"""relay.py: generalized f3 relay screen on an 8-state base machine.

usage: python relay.py BASE NAME [--slots A0,B1,..] [--npar 2] [--phase 1|2|12]
For every slot S of BASE (default: all defined slots), every replacement S' = (w', d', I), every common symbol c and
every I_c (36 options) the 9-state candidate with I_(1-c) undefined is tested for TRANSPARENCY:
  1a  blank tape, faithful world, first jump must equal BASE's first jump (engine intact);
  1b  from the marker-only context CTX (BASE's J3 configuration in the faithful world) the whole trace and the halt
      (ones) must equal BASE's, without reading I_(1-c).
Survivors (S, S', c, I_c) then get I_(1-c) in all 36 values (phase 2): blank tape, faithful world, full run.
Outputs runs/relay_<NAME>/p1.tsv, p2.tsv, per-run logs for phase 2 only.  Every pkf8 PID -> ../pids.txt, wall watchdog.
Faithful world: --B 6 --cls 366 --mod 3600 --cnt (B = 6 mod 2520, R = 366 mod 3600)."""
import subprocess, sys, os, time, re
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(BASE_DIR, 'tools', 'pkf8.exe')
WORLD = '--B 6 --cls 366 --mod 3600 --cnt'.split()
args = sys.argv[1:]
base, name = args[0], args[1]
opt = {}
i = 2
while i < len(args):
    opt[args[i][2:]] = args[i + 1]; i += 2
NPAR = int(opt.get('npar', 2))
PHASE = opt.get('phase', '12')
CTX = opt.get('ctx', '0,0,60,6,37,1*4394,0,2,z2,19,1*11;1;1100;12').split(';;')  # list of kt specs
WALL1, WALL2 = float(opt.get('wall1', 40)), float(opt.get('wall2', 150))
MAXS2 = opt.get('maxs2', '6e9')
odir = os.path.join(BASE_DIR, 'runs', 'relay_' + name); os.makedirs(odir, exist_ok=True)
pidf = open(os.path.join(BASE_DIR, 'pids.txt'), 'a')
SKIP = [s for s in opt.get('skip', '').split(',') if s]   # patterns "H0=0LI,I1=1RF" style handled by skipfn

def rows(m): return m.split('_')
def setslot(m, q, c, v):
    r = rows(m); r[q] = r[q][:3 * c] + v + r[q][3 * c + 3:]; return '_'.join(r)
def getslot(m, q, c): return rows(m)[q][3 * c:3 * c + 3]

def parse(text):
    """trace = list of (kind, t, k, view) per jump + ('HALT', state, ones) or other ending"""
    tr = []; end = 'RUNNING'
    for l in text.splitlines():
        if l.startswith('J'):
            f = l.split('|', 1); head = f[0].split(); view = f[1].strip() if len(f) > 1 else ''
            kind = head[1]; t = re.search(r' t=(\d+)', f[0]); k = re.search(r' k=(\d+)', f[0])
            tr.append((kind, t.group(1) if t else '', k.group(1) if k else '', view))
        elif l.startswith('HALT'):
            mo = re.search(r'ones (\d+)', l); end = ('HALT', l.split()[1], mo.group(1) if mo else '')
        elif l.startswith(('STOP', 'END', 'RCAP')): end = (l.split()[0], l.strip()[:80])
        elif 'bad_alloc' in l: end = ('BADALLOC',)
    return tr, end

import collections
TMP = os.path.join(odir, 'tmp'); os.makedirs(TMP, exist_ok=True)
class Pool:
    """job queue; callbacks may push follow-up jobs (front of the queue)"""
    def __init__(self, n): self.n = n; self.running = []; self.q = collections.deque(); self.ctr = 0
    def submit(self, m, extra, wall, cb, path=None, front=False):
        (self.q.appendleft if front else self.q.append)((m, extra, wall, cb, path))
    def start(self, job):
        m, extra, wall, cb, path = job
        tmp = path is None
        if tmp: self.ctr += 1; path = os.path.join(TMP, 'j%d.txt' % self.ctr)
        fo = open(path, 'w')
        p = subprocess.Popen([EXE, m] + extra, stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
        pidf.write('%d relay %s %s\n' % (p.pid, name, time.strftime('%H:%M:%S'))); pidf.flush()
        self.running.append([p, fo, time.time(), wall, cb, path, tmp])
    def run_all(self):
        while self.q or self.running:
            while self.q and len(self.running) < self.n: self.start(self.q.popleft())
            time.sleep(0.03)
            for r in self.running[:]:
                p = r[0]; killed = False
                if p.poll() is None and time.time() - r[2] > r[3]:
                    subprocess.call(['taskkill', '/PID', str(p.pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    killed = True; p.wait()
                if p.poll() is not None:
                    r[1].close(); txt = open(r[5], errors='replace').read()
                    if r[6]: os.remove(r[5])
                    self.running.remove(r); r[4](txt, killed)

OPTS = [w + d + chr(65 + s) for w in '01' for d in 'LR' for s in range(9)]
pool = Pool(NPAR)

# references
ref1 = parse(subprocess.run([EXE, base] + WORLD + ['--jumps', '1', '--maxs', '1e6'], capture_output=True, text=True).stdout)[0][:1]
refc = [parse(subprocess.run([EXE, base, '--kt', c, '--R', '366', '--cls', '366', '--mod', '3600', '--cnt'],
                             capture_output=True, text=True).stdout) for c in CTX]
print('ref J1', ref1, 'ctx ends', [r[1] for r in refc], flush=True)

base9 = base + '_------'
defined = [(q, c) for q in range(8) for c in range(2) if getslot(base, q, c)[0] != '-']
if 'slots' in opt: defined = [(ord(s[0]) - 65, int(s[1])) for s in opt['slots'].split(',')]

def skipfn(m):
    # y1-fable's F3 (H0=0LI, I1=1RF) and F4 (H0=0LI, I0=0RF) on M8
    if not opt.get('skipf34'): return False
    r = rows(m)
    return r[7][:3] == '0LI' and (r[8][3:6] == '1RF' or r[8][:3] == '0RF')

p1 = open(os.path.join(odir, 'p1.tsv'), 'a'); p2 = open(os.path.join(odir, 'p2.tsv'), 'a')
done1 = set(l.split('\t')[0] for l in open(os.path.join(odir, 'p1.tsv'))) if os.path.exists(os.path.join(odir, 'p1.tsv')) else set()
survivors = []
if '1' in PHASE:
    for (q, c0) in defined:
        for wd in ['0L', '0R', '1L', '1R']:
            root = setslot(base9, q, c0, wd + 'I')
            for c in (0, 1):
                for v in OPTS:
                    m = setslot(root, 8, c, v)
                    if m in done1: continue
                    tag = '%s%d=%sI c=%d I%d=%s' % (chr(65 + q), c0, wd, c, c, v)
                    def cb1(txt, killed, m=m, tag=tag, c=c):
                        tr, end = parse(txt)
                        if tr[:1] != ref1:
                            p1.write('%s\t%s\tJ1X\t%s\n' % (m, tag, end)); p1.flush(); return
                        # stage 1b, chained
                        def cb1b(txt2, killed2, ci=0):
                            tr2, end2 = parse(txt2)
                            if killed2 or (tr2, end2) != refc[ci]:
                                p1.write('%s\t%s\tCTXX%d\t%s\t%s\n' % (m, tag, ci, end2, len(tr2))); p1.flush(); return
                            if ci + 1 < len(CTX):
                                pool.submit(m, ['--kt', CTX[ci + 1], '--R', '366', '--cls', '366', '--mod', '3600', '--cnt'], WALL1,
                                            lambda t3, k3: cb1b(t3, k3, ci + 1), front=True); return
                            p1.write('%s\t%s\tPASS\n' % (m, tag)); p1.flush()
                        pool.submit(m, ['--kt', CTX[0], '--R', '366', '--cls', '366', '--mod', '3600', '--cnt'], WALL1, cb1b, front=True)
                    pool.submit(m, WORLD + ['--jumps', '1', '--maxs', '1e6'], 10, cb1)
    pool.run_all()
if '2' in PHASE:
    surv = [l.split('\t') for l in open(os.path.join(odir, 'p1.tsv')) if '\tPASS' in l]
    done2 = set(l.split('\t')[0] for l in open(os.path.join(odir, 'p2.tsv'))) if os.path.exists(os.path.join(odir, 'p2.tsv')) else set()
    k = 0
    for m, tag, _ in surv:
        c = int(tag.split('c=')[1][0])
        for v in OPTS:
            mm = setslot(m, 8, 1 - c, v)
            if skipfn(mm) or mm in done2: continue
            k += 1; nm = 'r%05d' % k
            while os.path.exists(os.path.join(odir, nm + '.txt')): k += 1; nm = 'r%05d' % k
            path = os.path.join(odir, nm + '.txt')
            def cb2(txt, killed, mm=mm, tag=tag, v=v, nm=nm):
                tr, end = parse(txt)
                ks = ' '.join(x[2] for x in tr if x[2])
                if len(ks) > 150: ks = ks[:60] + ' ... ' + ks[-80:]
                e = ('KILLED' if killed else '') + ' '.join(end)
                p2.write('\t'.join([mm, nm, tag + ' I%d=%s' % (1 - c, v), e, str(len(tr)), ks]) + '\n'); p2.flush()
            pool.submit(mm, WORLD + ['--maxs', MAXS2, '--jumps', '400', '--maxt', '1e11'], WALL2, cb2, path)
    pool.run_all()
print('done', flush=True)
