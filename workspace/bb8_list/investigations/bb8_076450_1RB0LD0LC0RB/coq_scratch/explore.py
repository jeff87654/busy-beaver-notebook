from planner import *
import sys


def coq_count(c, l):
    if not l:
        return str(c)
    if len(l) != 1 or l[0][1] != 1:
        return None
    t = l[0][0]
    for _ in range(c):
        t = 'S (%s)' % t
    return t


def apply_special(cfg):
    q, L, R, mode = cfg
    # E moving left over ones, with a 1 marker on its right:  l 1^k <E 1 r  ->  l <E 1 0^k r
    if mode == '<' and q == 'E' and is_run(L[0]) and set(L[0][1]) == {1} and R[0] == 1:
        blk, cnt = L[0][1], L[0][2]
        k = len(blk)
        nc = tuple((v, c * k) for v, c in cnt)
        return (q, L[1:], norm_side([1, ('run', (0,), nc)] + R[1:]), '<'), 'follow (cross_E1 %s).' % ('[' + ';'.join(map(str, blk)) + ']')
    return None


def drive(name, cfg, target, maxev=200, verbose=True):
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
            try:
                head(cfg)
            except Stuck:
                break
            cfg = step(cfg)
            n += 1
            if verbose > 1:
                print('     ', show(cfg))
            if n > 100000:
                raise RuntimeError('limit')
        if verbose:
            print('  [%3d steps] stuck: %s' % (n, show(cfg)))
        sp = apply_special(cfg)
        if sp is not None:
            cfg, lname = sp
            script.append('execute. ' + lname)
            if verbose:
                print('     special %s -> %s' % (lname, show(cfg)))
            continue
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


def P(a1, b1, a2, b2, t, c=None, rest=None):
    """0^inf E> 0 (10)^a1 11 0^b1 (10)^a2 11 0^b2 (10)^t 11 0^inf ; c = concrete extra counts"""
    c = c or {}
    R = [0] + mkrun((1, 0), a1, c.get('a1', 0)) + [1, 1] + mkrun((0,), b1, c.get('b1', 0))
    if rest is not None:
        R += rest
    else:
        R += mkrun((1, 0), a2, c.get('a2', 0)) + [1, 1] + mkrun((0,), b2, c.get('b2', 0)) + mkrun((1, 0), t, c.get('t', 0)) + [1, 1, BLANK]
    return ('E', [BLANK], norm_side(R), '>')


A1, B1, A2, B2, TT = {'a': 1}, {'b': 1}, {'c': 1}, {'d': 1}, {'t': 1}
Z = {}
r = [V('r')]

if __name__ == '__main__':
    which = sys.argv[1:] or ['R1']
    verbose = 2 if 'v' in which else 1
    if 'R1' in which:
        drive('R1', P(A1, B1, None, None, None, c={'b1': 2}, rest=r), P(A1, B1, None, None, None, c={'a1': 1, 'b1': 1}, rest=r), verbose=verbose)
    print()
    for nm, lm in sorted(LEMMAS.items()):
        print(nm, lm)


def P2(a1, b1, a2, b2, c=None, rest=None):
    c = c or {}
    R = [0] + mkrun((1, 0), a1, c.get('a1', 0)) + [1, 1] + mkrun((0,), b1, c.get('b1', 0))
    R += mkrun((1, 0), a2, c.get('a2', 0)) + [1, 1] + mkrun((0,), b2, c.get('b2', 0)) + rest
    return ('E', [BLANK], norm_side(R), '>')


if __name__ == '__main__':
    if 'R2' in which:
        drive('R2', P2(A1, Z, A2, B2, c={'a1': 1, 'b1': 1, 'b2': 2}, rest=r),
              P2(Z, {'a': 2}, A2, B2, c={'a1': 1, 'b1': 2, 'a2': 1, 'b2': 1}, rest=r), verbose=verbose)
    if 'R3' in which:
        drive('R3', P(A1, Z, A2, Z, TT, c={'a1': 1, 'b1': 1, 'b2': 1}),
              P(Z, Z, A1, {'c': 2}, TT, c={'a1': 1, 'b1': 2, 'b2': 3, 't': 1}), verbose=verbose)
    print()
    for nm, lm in sorted(LEMMAS.items()):
        print(nm, lm)
