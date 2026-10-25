import sys, itertools, collections
from kev import run_events
from kstep import kword

def toks(w):
    r = w[::-1]; out = []; i = 0
    while i + 1 < len(r):
        out.append({'11': 'S', '01': 'A', '10': 'a', '00': 'z'}[r[i:i+2]]); i += 2
    return out, r[i:]

def rle(t):
    return [(k, len(list(g))) for k, g in itertools.groupby(t)]
def fmt(r):
    return ' '.join(k if n == 1 else '%s^%d' % (k, n) for k, n in r)

def visits(ds, a, b, maxsteps, maxvis=400):
    w0 = kword(ds, a, b)
    out = []
    def cb(steps, xs, w):
        out.append((steps, w)); return len(out) > maxvis
    r = run_events(maxsteps, cb, init=(w0, len(w0), 2))
    if r[0] == 'HALT': out.append((r[1], 'HALT'))
    return out

pats = collections.defaultdict(list)
def feed(ds, a, b, maxsteps=300000, maxvis=300):
    vs = visits(ds, a, b, maxsteps, maxvis)
    for (s1, w1), (s2, w2) in zip(vs, vs[1:]):
        if w2 == 'HALT' or w1 == 'HALT': continue
        t1, r1 = toks(w1); t2, r2 = toks(w2)
        # keep marker/rest in the word: represent as tokens + ('M', rest)
        a1 = t1 + ['|' + r1]; a2 = t2 + ['|' + r2]
        i = 0
        while i < min(len(a1), len(a2)) and a1[-1 - i] == a2[-1 - i]: i += 1
        p1 = a1[:len(a1) - i]; p2 = a2[:len(a2) - i]
        pats[(fmt(rle(p1)), fmt(rle(p2)))].append(s2 - s1)

if __name__ == '__main__':
    for ds in [(), (1,), (2,), (1, 1), (0, 2), (1, 0, 1), (0, 0, 1), (2, 0, 0, 1), (0,), (0, 0), (0, 0, 0), (3,0,1)]:
        for a in (0, 1, 2):
            for b in (0, 1, 2, 3, 4):
                feed(ds, a, b)
    for k, v in sorted(pats.items(), key=lambda kv: -len(kv[1])):
        st = sorted(set(v))
        print('%-34s -> %-34s n=%d steps %s' % (k[0], k[1], len(v), st[:8]))
