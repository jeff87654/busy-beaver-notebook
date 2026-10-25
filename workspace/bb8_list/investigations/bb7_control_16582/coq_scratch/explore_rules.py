from planner import *
import sys

run = lambda blk, c: ('run', tuple(blk), lin({c: 1}))


def coq_count(c, l):
    """Coq term for count with c concrete blocks and linear part l."""
    if not l:
        return str(c)
    if len(l) != 1 or l[0][1] != 1:
        return None
    t = l[0][0]
    for _ in range(c):
        t = 'S (%s)' % t
    return t


def drive(name, cfg, target, maxev=80, verbose=True, use_L0s=True):
    print('=====', name)
    print('  start :', show(cfg))
    print('  target:', show(target))
    ct = canon(target)
    script = []
    for ev in range(maxev):
        n = 0
        while True:
            if canon(cfg) == ct:
                script.append('do %d step. finish_norm.' % n)
                print('  reached target after', n, 'steps')
                print('  SCRIPT:', ' '.join(script))
                return script
            m = match_L0s(cfg) if use_L0s else None
            if m and m[1][1]:
                (jc, jl), (kc, kl), rest, rot = m
                J, K = coq_count(jc, jl), coq_count(kc, kl)
                rw = ''
                for (x0, xs, cnt) in rot:
                    rw += ' rewrite (align_lpow %d [%s] _ %s). simpl app.' % (x0, ';'.join(map(str, xs)), coq_count(0, cnt))
                script.append('do %d step.%s follow (L0s %s %s).' % (n, rw, K, J))
                if verbose:
                    print('  [%3d steps] L0s at: %s' % (n, show(cfg)))
                cfg = apply_L0s(cfg)
                if verbose:
                    print('     -> %s' % show(cfg))
                n = 0
                continue
            try:
                head(cfg)
            except Stuck:
                break
            cfg = step(cfg)
            n += 1
            if n > 100000:
                raise RuntimeError('limit')
        if verbose:
            print('  [%3d steps] stuck: %s' % (n, show(cfg)))
        cfg, lname = apply_crossing(cfg)
        if isinstance(lname, tuple):
            _, x0, xs, cnt = lname
            script.append('execute. rewrite (align_lpow %d [%s] _ %s). simpl app.'
                          % (x0, ';'.join(map(str, xs)), coq_count(0, cnt)))
        else:
            script.append('execute. follow %s.' % lname)
        if verbose:
            print('     follow %s -> %s' % (lname, show(cfg)))
    print('  gave up')
    return script


def beta(x, j, k, r, xc=0, jc=0, kc=0):
    return ('A', [BLANK], [0, 0] + mkrun((1, 0, 0), x, xc) + [1, 0, 1, 0] + mkrun((1, 0, 0), j, jc) + [1, 0, 1, 0]
            + mkrun((1, 1, 0), k, kc) + [1, 0, 1, 0, 0] + r, '>')


def gamma(x, j, m, r, xc=0, jc=0, mc=0):
    return ('A', [BLANK], [0, 0] + mkrun((1, 0, 0), x, xc) + [1, 0, 1, 0] + mkrun((1, 0, 0), j, jc) + [1, 0]
            + mkrun((1, 0, 0), m, mc) + [0, 0, 1, 0, 0] + r, '>')


X, J, K, M = {'x': 1}, {'j': 1}, {'k': 1}, {'m': 1}
XX = {'x': 2}
Z = {}
r = [V('r')]

if __name__ == '__main__':
    which = sys.argv[1:] or ['L0', 'R1', 'T1', 'R2', 'T2']
    if 'L0' in which:
        start = ('A', [BLANK], [0, 0] + mkrun((1, 0, 0), J) + [1, 0, 1, 0] + mkrun((1, 1, 0), K, 1) + r, '>')
        target = ('A', [BLANK], [0, 0] + mkrun((1, 0, 0), J, 2) + [1, 0, 1, 0] + mkrun((1, 1, 0), K) + r, '>')
        drive('L0', start, target, use_L0s=False)
    if 'R1' in which:
        drive('R1', beta(X, J, K, r, kc=1), beta(XX, J, K, r, xc=3, jc=2))
    if 'T1' in which:
        drive('T1', beta(X, J, Z, r), gamma(XX, Z, J, [1, 0] + r, xc=3, mc=1))
    if 'R2' in which:
        drive('R2', gamma(X, J, M, r, mc=1), gamma(XX, J, M, r, xc=3, jc=2))
    if 'T2' in which:
        drive('T2', gamma(X, J, Z, r), beta(XX, Z, J, r, xc=3))
    print()
    for nm, lm in sorted(LEMMAS.items()):
        print(nm, lm)
