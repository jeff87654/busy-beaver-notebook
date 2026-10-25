# realj.py J1 J2 ...: I1 exhaustion (first CL or halt) for representatives n = real class mod 6*5^j (m = 0,1), R = 2000
import idle, sys
from gm import run
N = 61337390949400
for j in map(int, sys.argv[1:]):
    mod = 6 * 5**j; base = N % mod
    for m in (0, 1):
        n = base + m * mod
        r = run(f'1*{n};1;6002;6')
        s = r.get('view', r.get('tape', ''))[:400]
        print(j, m, n, 2000, r['kind'], 't=%s' % r.get('t'), 'step=%s' % r.get('step'), '|', s, flush=True)
