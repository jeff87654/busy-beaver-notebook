import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""roundfit.py OUT MACHINE --ks K1,K2.. --ts T1,T2.. --R R1,R2 [--cls C --mod M] [--par 2] [--jumps 400] [--maxs 3e9] [--old 1100]
Direct starts at Top(K) = '0*2 7 1*K' (pkf8 --kt '0*2,7,1*(K-1);1;OLD;T'), every fresh accumulator = R (class C mod M).
Per start: next Top view '0*2 7 1*K2' (K2 >= 100): K2, t2, #jumps to it, min clear depth on the way; or 'exit' + end line.
OUT tsv: machine K t R K2 t2 nj mink end.  Resumable (skips (machine,K,t,R) rows present).  PIDs -> pids.txt."""
import subprocess, re, time
a = sys.argv[1:]; OUT, M = a[0], a[1]; opt = dict(zip(a[2::2], a[3::2]))
KS = [int(x) for x in opt['--ks'].split(',')]; TS = [int(x) for x in opt['--ts'].split(',')]; RS = [int(x) for x in opt['--R'].split(',')]
CLS = opt.get('--cls', '66'); MODV = opt.get('--mod', '150'); PAR = int(opt.get('--par', '2')); JUMPS = opt.get('--jumps', '400')
MAXS = opt.get('--maxs', '3e9'); OLD = opt.get('--old', '1100'); EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
TMPD = os.path.join(BASE, 'runs', 'rf_tmp', M[-27:].replace('-', 'x')); os.makedirs(TMPD, exist_ok=True)
TOP = re.compile(r'\| 0\*2 7 1\*(\d+)$')
done = set()
if os.path.exists(OUT):
    for l in open(OUT): p = l.split('\t'); done.add(tuple(p[:4]))
jobs = [(K, t, R) for R in RS for t in TS for K in KS if (M, str(K), str(t), str(R)) not in done]
pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); fo = open(OUT, 'a'); run = []
def parse(txt):
    nj = 0; mink = 10 ** 9
    for l in txt.splitlines()[1:] if False else txt.splitlines():
        if not l.startswith('J'): continue
        nj += 1
        if nj == 1: continue
        mk = re.search(r' k=(\d+)', l)
        mm = TOP.search(l.rstrip())
        if mm and int(mm.group(1)) >= 100:
            t2 = re.search(r' t=(\d+)', l).group(1); return mm.group(1), t2, str(nj - 1), str(mink), ''
        if mk: mink = min(mink, int(mk.group(1)))
    end = [l for l in txt.splitlines() if l.startswith(('HALT', 'STOP', 'END'))]
    return 'exit', '', str(nj - 1), str(mink), (end[0][:50] if end else 'none')
while jobs or run:
    while jobs and len(run) < PAR:
        K, t, R = jobs.pop(0)
        kt = '0*2,7,1*%d;1;%s;%d' % (K - 1, OLD, t)
        tf = os.path.join(TMPD, '%d_%d_%d.txt' % (K, t, R)); fh = open(tf, 'w')
        p = subprocess.Popen([EXE, M, '--kt', kt, '--R', str(R), '--cls', CLS, '--mod', MODV, '--cnt', '--jumps', JUMPS, '--maxs', MAXS, '--maxt', MAXS, '--view', '200'],
                             stdout=fh, stderr=subprocess.STDOUT, creationflags=0x40)
        p.tf = tf; p.fh = fh
        pidf.write('%d pkf8 roundfit %s K=%d t=%d R=%d\n' % (p.pid, M[-13:], K, t, R)); pidf.flush()
        run.append((p, K, t, R))
    time.sleep(0.2)
    for r in list(run):
        if r[0].poll() is not None:
            run.remove(r); r[0].fh.close(); res = parse(open(r[0].tf, errors='replace').read()); os.remove(r[0].tf)
            fo.write('\t'.join([M, str(r[1]), str(r[2]), str(r[3])] + list(res)) + '\n'); fo.flush()
