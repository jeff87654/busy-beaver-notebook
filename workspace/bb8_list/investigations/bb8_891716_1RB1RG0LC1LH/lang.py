import sys, collections
from kev import run_events
N = int(sys.argv[1])
cnt = collections.Counter(); bad = []
def lt(w):
    # left-aligned: marker 1, pairs from left, optional dangling 1
    if not w or w[0] != '1': return None
    s = w[1:]; toks = []
    i = 0
    while i + 1 < len(s):
        p = s[i:i+2]
        if p not in ('10', '11'): return None
        toks.append('U' if p == '10' else 'S'); i += 2
    dang = s[i:]
    if dang not in ('', '1'): return None
    return ''.join(toks), dang
n = [0]
def cb(steps, xs, w):
    n[0] += 1
    r = lt(w)
    if r is None:
        bad.append((steps, w[:60]))
    else:
        cnt[r[1]] += 1
    return False
run_events(N, cb)
print('visits', n[0], 'dangling stats', dict(cnt), 'bad', len(bad)); print(bad[:10])
