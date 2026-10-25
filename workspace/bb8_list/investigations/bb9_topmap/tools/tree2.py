import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""tree2.py [NPAR] [JUMPS] [MAXT] [WALL] [VARIANTS...]: TNF-style tree over the slots H1, I0, I1 of
   1RB0RA_1LC1LF_1RD0LB_1RA1LE_<E0>0LC_1RG1LD_0RG0RF_<H0><H1>_<I0><I1>   (M8 engine), variants E0_H0 (default all four of
   {0LH,1LH} x {0LI,1LI}).  Root: H1 = I0 = I1 undefined; a run that halts on an undefined slot while another slot is still
   undefined is expanded over the 36 values of that slot.  Before a run, backref (depth 20) on the undefined slots: if all
   are UNREACHABLE the node is recorded BR-NOHALT without running.  World W3: --B 366 --cls 366 --mod 3600 --cnt.
   Output: runs/A_<E0>_<H0>/<id>.txt (id = H1 I0 I1 with - -> x) and tree.tsv: id machine outcome jumps ones ntops tops zeros.
   Resumes from tree.tsv (also reads tree.py's old 6-char ids)."""
import subprocess, time, re, collections
sys.path.insert(0, os.path.join(BASE, 'tools')); from backref_s import check
NPAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2
JUMPS = sys.argv[2] if len(sys.argv) > 2 else '20'
MAXT = sys.argv[3] if len(sys.argv) > 3 else '1.2e9'
WALL = float(sys.argv[4]) if len(sys.argv) > 4 else 30
VARS = sys.argv[5:] or ['0LH_0LI', '1LH_0LI', '0LH_1LI', '1LH_1LI']
EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
VALS = [w + d + s for w in '01' for d in 'LR' for s in 'ABCDEFGHI']
TOP = re.compile(r'^(0\*\d+|0) (1 )?7 (z2 \d+ )?1\*(\d+)$')
def summarize(path):
    out = 'KILLED'; ones = ''; zeros = ''; nj = 0; tops = []
    for l in open(path, errors='replace'):
        if l.startswith('J'):
            nj += 1
            if '|' in l:
                mm = TOP.match(l.split('|', 1)[1].strip())
                if mm and int(mm.group(4)) >= 1000: tops.append(mm.group(4))
        elif l.startswith('HALT'): out = 'HALT ' + l.split()[1]; mo = re.search(r'ones (\d+)', l); ones = mo.group(1) if mo else ''
        elif l.startswith('STOP'): out = 'STOP'
        elif l.startswith('END'): out = 'END'
        elif l.startswith('zeros:'): zeros = l[6:].strip()
    return out, nj, ones, tops, zeros
pidf = open(os.path.join(BASE, 'pids.txt'), 'a')
pidf.write('%d driver tree2.py %s %s\n' % (os.getpid(), ' '.join(VARS), time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
SL = ['H1', 'I0', 'I1']
for var in VARS:
    E0, H0 = var.split('_')
    ODIR = os.path.join(BASE, 'runs', 'A_' + var); os.makedirs(ODIR, exist_ok=True)
    TSV = os.path.join(ODIR, 'tree.tsv')
    def mach(s): return '1RB0RA_1LC1LF_1RD0LB_1RA1LE_%s0LC_1RG1LD_0RG0RF_%s%s_%s%s' % (E0, H0, s[0], s[1], s[2])
    done = {}
    if os.path.exists(TSV):
        for l in open(TSV):
            p = l.rstrip('\n').split('\t')
            if len(p) >= 3: done[p[1]] = p[2]
    tsv = open(TSV, 'a')
    def expand(s, out):
        und = [i for i in range(3) if s[i] == '---']
        if not out.startswith('HALT ') or len(und) < 2: return
        i = SL.index(out.split()[1])
        if s[i] != '---': return
        for v in VALS:
            n = list(s); n[i] = v; pend.append(tuple(n))
    pend = collections.deque([('---', '---', '---')]); running = []; seen = set()
    while pend or running:
        while pend and len(running) < NPAR:
            s = pend.popleft(); m = mach(s)
            if m in seen: continue
            seen.add(m)
            if m in done: expand(s, done[m]); continue
            mid = ''.join(s).replace('-', 'x')
            und = [SL[i] for i in range(3) if s[i] == '---']
            br = dict(check(m, 20, maxnodes=20000))
            if all(br.get(x, '').startswith('UNREACHABLE') for x in und):
                done[m] = 'BR-NOHALT'; tsv.write('\t'.join([mid, m, 'BR-NOHALT', '0', '', '0', '', '']) + '\n'); tsv.flush(); continue
            path = os.path.join(ODIR, mid + '.txt'); fo = open(path, 'w')
            p = subprocess.Popen([EXE, m, '--B', '366', '--cls', '366', '--mod', '3600', '--cnt', '--jumps', JUMPS, '--maxs', '1e9', '--maxt', MAXT, '--view', '300'],
                                 stdout=fo, stderr=subprocess.STDOUT, creationflags=0x40)
            pidf.write('%d pkf8 %s %s %s\n' % (p.pid, var, mid, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
            running.append([p, fo, s, m, mid, path, time.time()])
        time.sleep(0.2)
        for r in list(running):
            p = r[0]
            if p.poll() is None and time.time() - r[6] > WALL:
                subprocess.call(['taskkill', '/PID', str(p.pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); p.wait()
            if p.poll() is not None:
                r[1].close(); running.remove(r)
                out, nj, ones, tops, zeros = summarize(r[5]); done[r[3]] = out
                tsv.write('\t'.join([r[4], r[3], out, str(nj), ones, str(len(tops)), ','.join(tops), zeros]) + '\n'); tsv.flush()
                expand(r[2], out)
    tsv.close()
    print('tree done', var, flush=True)
print('all done', flush=True)
