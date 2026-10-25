"""screen.py SHARD NSHARD [--maxt 1e7] [--M 60] [--out scr] : tier-1 screen of M8-recipe children.

For every base (xcands.json order, i % NSHARD == SHARD) with its tower class (towercls_*.jsonl, template = towercls tmpl):
  free slot X:   for each (w,d): child = base with X -> (w,d,H), H = ------ ; FREE = H0,H1 (TNF branching in wf3)
  guard (X,s):   child = base with X -> (wX,dX,H), H(1-s) = T(1-s), H(s) = --- ; FREE = H<s>
Snapshot: base run in the world up to its first read of X (shared by the variants of X).
Results: OUT/<i>_<X>[_g<s>|_<w><d>].txt (leaf lines), OUT/<i>.json (per-base summary), resumable.
"""
import sys, os, json, time, subprocess, argparse, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, 'wf8.exe')
IDLE = 0x40


def logpid(p, cmd):
    with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
        pf.write('%d\t%s\t%s\n' % (p.pid, time.strftime('%Y-%m-%d %H:%M:%S'), ' '.join(cmd)[:200]))


def run(cmd, out):
    with open(out, 'w') as fo:
        p = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.STDOUT, creationflags=IDLE | 0x08000000, cwd=HERE)
        logpid(p, cmd)
        p.wait()
    return open(out).read()


def tclasses():
    tc = {}
    for f in glob.glob(os.path.join(HERE, 'towercls_*.jsonl')):
        for l in open(f):
            try:
                o = json.loads(l)
            except Exception:
                continue
            tc[o['machine']] = o
    return tc


def setslot(m, X, act):
    R = m.split('_')
    st, sym = ord(X[0]) - 65, int(X[1])
    R[st] = R[st][:3 * sym] + act + R[st][3 * sym + 3:]
    return '_'.join(R)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shard', type=int); ap.add_argument('nshard', type=int)
    ap.add_argument('--maxt', default='auto'); ap.add_argument('--maxs', default='1e7')
    ap.add_argument('--M', type=int, default=60); ap.add_argument('--rc', default='10')
    ap.add_argument('--out', default='scr'); ap.add_argument('--snapmaxt', default='3e9')
    ap.add_argument('--only', default=None, help='comma list of base indices')
    ap.add_argument('--xc', default='xcands.json')
    a = ap.parse_args()
    out = os.path.join(HERE, a.out); os.makedirs(out, exist_ok=True)
    rows = json.load(open(os.path.join(HERE, a.xc)))
    tc = tclasses()
    only = set(int(x) for x in a.only.split(',')) if a.only else None
    for r in rows:
        i = r['i']
        if only is not None and i not in only:
            continue
        if only is None and i % a.nshard != a.shard:
            continue
        sf = os.path.join(out, '%03d.json' % i)
        if os.path.exists(sf):
            continue
        if not r['free'] and not r['guards']:
            json.dump({'i': i, 'm': r['m'], 'skip': 'no exhaustion-only slot or guard pair'}, open(sf, 'w'))
            continue
        o = tc.get(r['m'])
        if not o:
            continue   # tower class not computed yet: retry on a later pass
        if 'cls' not in o or not o['cls']:
            json.dump({'i': i, 'm': r['m'], 'skip': 'no tower class (%s)' % o.get('err')}, open(sf, 'w'))
            continue
        tmpl = o.get('tmpl') or r['tmpl']
        cl = sorted(set(c % a.M for c in o['cls']))
        summ = {'i': i, 'm': r['m'], 'tmpl': tmpl, 'cls': o['cls'], 'M': a.M, 'runs': []}
        t0 = time.time()
        for c in cl:
            r0 = c if c >= 4 else c + a.M
            common = ['--rc', a.rc, '--rk', '1', '--cls', str(c), str(a.M), '--R0', str(r0)]
            if tmpl.startswith('R,B,P=11,u=10,s=1,d=3d+1,b=3b+2'):
                common += ['--tail', '11/11111100/1001']
            xs = [(X, None) for X in r['free']] + [(g[:2], int(g[2])) for g in r['guards']]
            for X, s in xs:
                tag = '%03d_%s_c%d' % (i, X, c)
                snapf = os.path.join(out, tag + '_snap.txt')
                if not os.path.exists(snapf) or 'SNAPPED' not in open(snapf).read():
                    so = run([WF, r['m'], tmpl] + common + ['--x', X, '--snapx', '--maxt', a.snapmaxt, '--maxs', a.snapmaxt], snapf)
                else:
                    so = open(snapf).read()
                if 'SNAPPED' not in so:
                    summ['runs'].append({'X': X, 's': s, 'c': c, 'snap': 'NOT REACHED: ' + so.strip().splitlines()[-1][-200:]})
                    continue
                f = so.split('\n')[0].split()
                snap = {'step': int(f[4]), 'nj': int(f[5]), 'maxk': int(f[6]), 'nesc': int(f[7]), 'R': int(f[8])}
                old = r['m'].split('_')[ord(X[0]) - 65][3 * int(X[1]):3 * int(X[1]) + 3]
                if s is None:
                    variants = [('%s%s' % (w, d), setslot(r['m'], X, w + d + 'H') + '_------', 'H0,H1') for w in '01' for d in 'LR']
                else:
                    if old[0] == '-':
                        continue
                    T = r['m'].split('_')[ord(old[2]) - 65]
                    copy = T[3 * (1 - s):3 * (1 - s) + 3]
                    h = ['---', '---']; h[1 - s] = copy
                    variants = [('g%d' % s, setslot(r['m'], X, old[:2] + 'H') + '_' + h[0] + h[1], 'H%d' % s)]
                for vt, child, free in variants:
                    rf = os.path.join(out, '%s_%s.txt' % (tag, vt))
                    if not os.path.exists(rf):
                        mt = a.maxt if a.maxt != 'auto' else ('1e7' if tmpl.startswith('R,B,P=11,u=10,s=1,d=3d+1,b=3b+2') else '3e6')
                        run([WF, child, tmpl] + common + ['--x', X, '--from', snapf, '--free', free, '--maxt', mt,
                                                           '--maxs', mt, '--loop', '--slit', '3e6', '--maxexact', '1e7', '--xmax', '20000', '--tapemax', '3e7'], rf)
                    summ['runs'].append({'X': X, 's': s, 'c': c, 'v': vt, 'snap': snap, 'file': os.path.basename(rf)})
        summ['time'] = round(time.time() - t0, 1)
        json.dump(summ, open(sf, 'w'))


if __name__ == '__main__':
    main()
