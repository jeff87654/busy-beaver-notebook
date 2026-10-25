"""p2.py: phase-2 analysis for exhaustions that leave the template (reb7 'T').
  python p2.py MACHINE TMPL1 [--n N] [--a0 0|1] [--bs b1,b2,..] [--steps 5000000]
1. tinf.exe: template inference on the run after the exhaustion K_T1(0^n; a0; b)
2. for each candidate template T2: xprobe.exe from the exhaustion to the first T2 K-moment for several b; keep T2 when
   every b lands in T2 and the entry configuration is affine per class (list struct like fit_E)
3. fit T2's rules (fit7.fit_rules) and its exhaustion map; report."""
import idle  # noqa: F401
import argparse
import subprocess
import os
import fit7

HERE = os.path.dirname(os.path.abspath(__file__))
TINF = os.path.join(HERE, 'tinf.exe')
XPR = os.path.join(HERE, 'xprobe.exe')


def ta(t):
    return fit7.targs(fit7.parse_template(t))


def tinf(m, t1, ds, a, b, skip, steps):
    inp = '%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b)
    p = subprocess.run([TINF, m] + ta(t1) + [str(skip), str(steps)], input=inp, capture_output=True, text=True,
                       creationflags=0x40, timeout=3600)
    return [l.split(None, 1)[1].strip() for l in p.stdout.splitlines() if l.startswith('TMPL')], \
        [l for l in p.stdout.splitlines() if not l.startswith('TMPL')]


def xprobe(m, t1, t2, cfgs, N):
    inp = ''.join('%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b) for ds, a, b in cfgs)
    p = subprocess.run([XPR, m] + ta(t1) + ta(t2) + [str(N)], input=inp, capture_output=True, text=True,
                       creationflags=0x40, timeout=7200)
    out = []
    for l in p.stdout.splitlines():
        f = l.split()
        if f[0] == 'K':
            out.append(('K', [] if f[1] == '-' else [int(x) for x in f[1].split(',')], int(f[2]), int(f[3]), int(f[4])))
        elif f[0] == 'H':
            out.append(('H', int(f[1])))
        else:
            out.append(('T',))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('t1')
    ap.add_argument('--n', type=int, default=0)
    ap.add_argument('--a0', type=int, default=0)
    ap.add_argument('--bs', default='60,61,62,63,64,65,66,67,68,69,70,71')
    ap.add_argument('--steps', type=int, default=5000000)
    ap.add_argument('--N', type=int, default=50000000)
    ap.add_argument("--maxt", type=int, default=40)
    ap.add_argument("--maxfit", type=int, default=40)
    args = ap.parse_args()
    m, t1 = args.machine, args.t1
    ds = [0] * args.n
    bs = [int(x) for x in args.bs.split(',')]
    cands, other = tinf(m, t1, ds, args.a0, bs[0], 0, args.steps)
    print('tinf: %d candidate templates; %s' % (len(cands), other))
    good = []
    for t2 in cands[:args.maxt]:
        res = xprobe(m, t1, t2, [(ds, args.a0, b) for b in bs], args.N)
        kinds = ''.join(r[0] for r in res)
        if set(kinds) != {'K'}:
            continue
        lens = [len(r[1]) for r in res]
        good.append((t2, res))
        print('T2 %s  entries: %s' % (t2, ' | '.join('b=%d n=%d %s a=%d b=%d @%d' % (b, len(r[1]), r[1][:8], r[2], r[3], r[4])
                                                   for b, r in list(zip(bs, res))[:4])))
    print('%d templates reached by every probe' % len(good))
    for t2, res in good[:args.maxfit]:
        P2 = fit7.Prober(m, t2)
        try:
            R2 = fit7.fit_rules(P2)
            print('FIT %s: D %s R2 a=%s b=%s Bpat %s MB %s nE %s mscan %s' % (
                t2, R2['F0'], R2['A2'], R2['B2'], {k: R2['Bpat'][k] for k in ('pre', 'm', 'x0', 'x1', 'head', 'mid', 'end', 'a', 'b')},
                bool(R2.get('MB')), R2.get('nE'), R2.get('mscan')))
        except fit7.FitError as e:
            print('NOFIT %s: %s' % (t2, e))


if __name__ == '__main__':
    main()
