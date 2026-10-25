"""sweep.py: M8-recipe children of one 7-state base, screened in the world follower.

  python sweep.py BASE TEMPLATE X MODE OUTDIR [--cls C M] [--world "extra wf args"] [--maxt N]

MODE  free       X -> (w,d,H) for all 4 (w,d); H0,H1 in {halt} + 32 actions (targets A..H); at least one halt slot in
                 the machine (the base's undefined slots other than X count only if X is not the base's only one).
      guardS     (S = 0/1, the symbol read right after X at the exhaustion): X keeps (w,d) and points to H;
                 H(1-S) = the original target's action on 1-S (engine copy); H(S) in {halt} + 32 actions.
Steps: snapshot of the base at its first read of X (wf --snapx), then every child from the snapshot (wf --batch --from).
Output: OUTDIR/children.txt, snap.txt, res.txt (one wf line per child), summary.json.
"""
import sys, os, subprocess, json, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, 'wf7.exe')
ACTS8 = ['%d%s%s' % (w, d, t) for w in (0, 1) for d in 'LR' for t in 'ABCDEFGH']
IDLE = 0x40


def rows(m):
    return m.split('_')


def children(base, X, mode):
    R = rows(base)
    st, sym = ord(X[0]) - 65, int(X[1])
    old = R[st][3 * sym:3 * sym + 3]
    undefined = [(i, c) for i, r in enumerate(R) for c in (0, 1) if r[3 * c] == '-']
    other_halt = any((i, c) != (st, sym) for i, c in undefined)
    out = []
    if mode == 'free':
        for w in '01':
            for d in 'LR':
                Xn = w + d + 'H'
                for h0 in ['---'] + ACTS8:
                    for h1 in ['---'] + ACTS8:
                        if not other_halt and h0 != '---' and h1 != '---':
                            continue
                        RR = list(R)
                        RR[st] = RR[st][:3 * sym] + Xn + RR[st][3 * sym + 3:]
                        out.append('_'.join(RR + [h0 + h1]))
    else:
        S = int(mode[-1])
        if old[0] == '-':
            raise SystemExit('guard mode needs a defined X')
        T = ord(old[2]) - 65
        copy = R[T][3 * (1 - S):3 * (1 - S) + 3]
        Xn = old[:2] + 'H'
        for hs in ['---'] + ACTS8:
            RR = list(R)
            RR[st] = RR[st][:3 * sym] + Xn + RR[st][3 * sym + 3:]
            h = [None, None]
            h[1 - S] = copy
            h[S] = hs
            out.append('_'.join(RR + [h[0] + h[1]]))
    return sorted(set(out))


def run(cmd, out, timeout=None):
    with open(out, 'w') as fo:
        p = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.STDOUT, text=True, creationflags=IDLE | 0x08000000)
        with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
            pf.write('%d\t%s\t%s\n' % (p.pid, time.strftime('%Y-%m-%d %H:%M:%S'), ' '.join(cmd)[:200]))
        p.wait(timeout=timeout)
    return open(out).read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('tmpl'); ap.add_argument('X'); ap.add_argument('mode'); ap.add_argument('outdir')
    ap.add_argument('--cls', nargs=2, type=int)
    ap.add_argument('--world', default='--rc 10 --rk 1')
    ap.add_argument('--maxt', default='2e9')
    ap.add_argument('--maxs', default='1e9')
    ap.add_argument('--tail', default=None)
    ap.add_argument('--jumps', default='3000000')
    ap.add_argument('--snapmaxt', default='6e9')
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    ch = children(a.base, a.X, a.mode)
    open(os.path.join(a.outdir, 'children.txt'), 'w').write('\n'.join(ch) + '\n')
    common = a.world.split()
    if a.cls:
        common += ['--cls', str(a.cls[0]), str(a.cls[1])]
    if a.tail:
        common += ['--tail', a.tail]
    common += ['--x', a.X, '--slots']
    snapf = os.path.join(a.outdir, 'snap.txt')
    t0 = time.time()
    so = run([WF, a.base, a.tmpl] + common + ['--snapx', '--maxt', a.snapmaxt, '--maxs', a.snapmaxt], out=snapf)
    summ = {'base': a.base, 'tmpl': a.tmpl, 'X': a.X, 'mode': a.mode, 'n': len(ch), 'world': common}
    if 'SNAPPED' not in so:
        summ['snap'] = 'FAILED: ' + so.strip().splitlines()[-1][:300]
        json.dump(summ, open(os.path.join(a.outdir, 'summary.json'), 'w'))
        print(json.dumps(summ))
        return
    summ['snap_line'] = [l for l in so.splitlines() if l.startswith('SNAP ')][0][:0] + so.splitlines()[0].split(' ', 2)[2][-120:] if False else ''
    f = so.split('\n')[0].split()
    summ['snap'] = {'step': int(f[4]), 'nj': int(f[5]), 'maxk': int(f[6]), 'nesc': int(f[7]), 'R': int(f[8]), 'width': len(f[1])}
    res = run([WF, '--batch', os.path.join(a.outdir, 'children.txt'), a.tmpl] + common +
              ['--from', snapf, '--maxt', a.maxt, '--maxs', a.maxs, '--jumps', a.jumps], out=os.path.join(a.outdir, 'res.txt'))
    summ['time'] = round(time.time() - t0, 1)
    cnt = {}
    for l in res.splitlines():
        f = l.split()
        if len(f) < 2:
            continue
        k = f[1]
        esc = [x for x in f if x.startswith('esc=')]
        e = int(esc[0][4:]) if esc else -1
        cnt['%s esc%d' % (k, e)] = cnt.get('%s esc%d' % (k, e), 0) + 1
    summ['outcomes'] = cnt
    json.dump(summ, open(os.path.join(a.outdir, 'summary.json'), 'w'))
    print(json.dumps(summ))


if __name__ == '__main__':
    main()
