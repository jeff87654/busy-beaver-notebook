import sys, re
from lit import Sim, MAIN, ST
N = int(sys.argv[1]); st = sys.argv[2] if len(sys.argv) > 2 else 'E'
UNITS = sys.argv[3].split(',') if len(sys.argv) > 3 else ['10', '1011']
s = Sim(MAIN, 1 << 22)
def tok(x):
    out = []; i = 0
    while i < len(x):
        best = None
        for u in UNITS:
            j = i
            while x.startswith(u, j): j += len(u)
            k = (j - i)//len(u)
            if k >= 2 and (best is None or k*len(u) > best[1]*len(best[0])): best = (u, k)
        if best:
            out.append('(%s)^%d' % best); i += best[1]*len(best[0])
        else:
            out.append(x[i]); i += 1
    r = []
    for t in out:
        if len(t) == 1 and r and len(r[-1]) < 12 and not r[-1].startswith('('): r[-1] += t
        else: r.append(t)
    return ' '.join(r)
prev = None
while s.steps < N:
    hi0 = s.hi
    if not s.step():
        print('HALT at', s.steps, s.ones()); break
    if s.pos > hi0 and ST[s.state] == st:
        t = s.tape; lo = s.lo
        while t[lo] == 0 and lo < s.pos: lo += 1
        L = ''.join(map(str, t[lo:s.pos]))
        T = tok(L)
        # skip boring transfers
        m = re.search(r'\(10\)\^(\d+) 1 \(10\)\^(\d+)$', T)
        key = re.sub(r'\(10\)\^\d+ 1 \(10\)\^\d+$', '', T) if m else None
        if m and key == prev: continue
        prev = key
        print(s.steps, s.pos - lo, T, '[%s]' % st, flush=True)
