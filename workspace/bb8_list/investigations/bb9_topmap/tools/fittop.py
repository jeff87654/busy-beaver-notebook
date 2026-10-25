import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""fittop.py OUT MACHINE VIEW T [--ks K1,K2..] [--R 366,3966] [--par N] [--jumps J] [--maxs S] [--cls C --mod M (default 366 3600)]: direct Top(K) starts.
VIEW = a top view from a blank-tape run with K replaced by K, e.g. '0*2 7 1*K' (tokens far-first; zN = gap).
Start = pkf8 --kt '<tokens with 1*K -> 1*(K-1)>;1;1100;T' (old accumulator 1100), fresh R per --R (all = 366 mod 3600).
Per start, records the next view of the same shape (same tokens, any K' >= 200) = next top, or 'exit' + the views seen and the end.
Appends rows to OUT (tsv: machine view T K R next views end); skips rows already in OUT.  PIDs -> pids.txt."""
import subprocess, re, time
args = sys.argv[1:]; OUT, M, VIEW, T = args[:4]
opt = dict(zip(args[4::2], args[5::2]))
KS = [int(x) for x in opt.get('--ks', ','.join(str(5000 + i) for i in range(25))).split(',')]
RS = [int(x) for x in opt.get('--R', '366').split(',')]
CLS = opt.get('--cls', '366'); MODV = opt.get('--mod', '3600'); PAR = int(opt.get('--par', '2')); JUMPS = opt.get('--jumps', '10'); MAXS = opt.get('--maxs', '8e9')
EXE = os.path.join(BASE, 'tools', 'pkf8.exe')
toks = VIEW.split()
assert toks[-1] == '1*K'
def kt(K, t): return ','.join(toks[:-1] + ['1*%d' % (K - 1)]) + ';1;1100;%s' % t
shape = re.compile('^' + ' '.join(re.escape(x) for x in toks[:-1]) + r' 1\*(\d+)$')
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        p = l.split('\t'); done.add(tuple(p[:5]))
jobs = [(K, R) for R in RS for K in KS if (M, VIEW, T, str(K), str(R)) not in done]
pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); fo = open(OUT, 'a'); run = []
def parse(txt):
    J = [l for l in txt.splitlines() if l.startswith('J')][1:]; vs = []; nxt = 'exit'
    for l in J:
        v = l.split('|', 1)[1].strip(); mm = shape.match(v)
        if mm and int(mm.group(1)) >= 200: nxt = mm.group(1); break
        vs.append(v[:60])
    end = [l for l in txt.splitlines() if l.startswith(('HALT', 'STOP', 'END'))]
    return nxt, ' // '.join(vs), (end[0][:60] if end else 'none')
while jobs or run:
    while jobs and len(run) < PAR:
        K, R = jobs.pop(0)
        p = subprocess.Popen([EXE, M, '--kt', kt(K, T), '--R', str(R), '--cls', CLS, '--mod', MODV, '--cnt', '--jumps', JUMPS, '--maxs', MAXS, '--view', '200'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=0x40)
        pidf.write('%d pkf8 fittop %s K=%d R=%d %s\n' % (p.pid, M[-13:], K, R, time.strftime('%m-%d %H:%M:%S'))); pidf.flush()
        run.append((p, K, R))
    time.sleep(0.3)
    for r in list(run):
        if r[0].poll() is not None:
            run.remove(r); nxt, vs, end = parse(r[0].stdout.read())
            fo.write('\t'.join([M, VIEW, T, str(r[1]), str(r[2]), nxt, vs, end]) + '\n'); fo.flush()
