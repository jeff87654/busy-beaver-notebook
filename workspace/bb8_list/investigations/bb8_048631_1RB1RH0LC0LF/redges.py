import sys, re
from lit import Sim, MAIN, ST
N = int(sys.argv[1]); st = sys.argv[2] if len(sys.argv) > 2 else 'E'
s = Sim(MAIN, 1 << 20)
def tok(x):
    # tokenise tape string greedily into 10-runs
    out = []; i = 0
    while i < len(x):
        if x.startswith('10', i):
            j = i
            while x.startswith('10', j): j += 2
            k = (j - i)//2
            out.append('(10)^%d' % k if k > 1 else '10'); i = j
        else:
            out.append(x[i]); i += 1
    r = []
    for t in out:
        if len(t) == 1 and r and len(r[-1]) < 12 and not r[-1].startswith('('): r[-1] += t
        else: r.append(t)
    return ' '.join(r)
while s.steps < N:
    hi0 = s.hi
    if not s.step():
        print('HALT at', s.steps, s.ones()); break
    if s.pos > hi0 and ST[s.state] == st:
        t = s.tape; lo = s.lo
        while t[lo] == 0 and lo < s.pos: lo += 1
        L = ''.join(map(str, t[lo:s.pos]))
        print(s.steps, s.pos - lo, tok(L), '[%s]' % st, flush=True)
