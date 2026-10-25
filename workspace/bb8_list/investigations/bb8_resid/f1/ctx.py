"""ctx.py MACHINE OUT NPAR : run MACHINE (pkf6) over a grid of endgame contexts (C04 real-like far tokens, small P), print
one summary line per context.  Contexts: far = 0,0,1077,4,645,6,385,6,229,19749,2,77 (C04's) or variants; P in PLIST; k in KLIST."""
import subprocess, sys, os, re, time, itertools
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m, out, npar = sys.argv[1], sys.argv[2], int(sys.argv[3])
FARS = {'c04': '0,0,1077,4,645,6,385,6,229,19749,2,77', 'c04b': '0,0,1078,4,646,6,386,6,230,19750,2,77',
        'c04c': '0,0,1079,4,647,6,387,6,231,19751,2,77', 'sm': '0,0,107,4,64,6,38,6,22,1974,2,77'}
PL = [int(x) for x in os.environ.get('CTX_P', '60,61,62,63,64,65').split(',')]; KL = [int(x) for x in os.environ.get('CTX_K', '18,24,12,42,6').split(',')]
FSEL = os.environ.get('CTX_FARS', ','.join(FARS)).split(',')
jobs = [(f, P, k) for f in FSEL for P in PL for k in KL]
pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); fo = open(out, 'a'); running = []
def summ(txt):
    ds = []; res = 'RUN'
    for l in txt.splitlines():
        if l.startswith('J'):
            mk = re.search(r' (CL|R1) .*?(?: k=(\d+))?', l); kk = re.search(r' k=(\d+)', l)
            ds.append(kk.group(1) if (kk and ' CL ' in l) else 'R1')
        elif l.startswith(('HALT', 'STOP', 'END')): res = ' '.join(l.split()[:2]) + (' ' + re.search(r'ones (\d+)', l).group(1) if 'ones' in l else '')
    comp = []
    for d in ds:
        if comp and comp[-1][0] == d: comp[-1][1] += 1
        else: comp.append([d, 1])
    s = ' '.join(d if c == 1 else '%sx%d' % (d, c) for d, c in comp)
    return res, (s if len(s) < 400 else s[:150] + ' ... ' + s[-240:])
while jobs or running:
    while jobs and len(running) < npar:
        f, P, k = jobs.pop(0)
        tmpf = out + '.tmp_%s_%d_%d' % (f, P, k)
        kt = '%s,1*%d,0,2,z2,1*%d;1;20;18' % (FARS[f], P, k)
        p = subprocess.Popen([os.path.join(BASE, 'pkf6.exe'), m, '--kt', kt, '--rk', '1', '--rc', '10', '--rmod', '36', '--exactcap', '1000',
                              '--jumps', '30000', '--maxt', '3e10', '--maxs', '1e10', '--rcap', '100000000', '--view', '200'], stdout=open(tmpf, 'w'), stderr=subprocess.STDOUT)
        pidf.write('%d ctx.py %s %s P=%d k=%d\n' % (p.pid, m[-12:], f, P, k)); pidf.flush(); running.append((p, f, P, k, tmpf))
    time.sleep(0.5)
    for r in running[:]:
        if r[0].poll() is None: continue
        running.remove(r); txt = open(r[4]).read(); os.remove(r[4]); res, s = summ(txt)
        fo.write('%s\tP=%d\tk=%d\t%s\t%s\n' % (r[1], r[2], r[3], res, s)); fo.flush()
