"""Probe resets: from 0^inf A>0 1^n 000 1^j 0^inf, run to the next S-form A0 config at the left edge
S(n,k,j) = A>0 1^n (001)^k 000 1^j."""
import re, sys
from lit import Sim, MAIN, compress, ST

SRE = re.compile(r'^(1*)((?:001)*)0001*$')

def run(word, tm=MAIN, maxsteps=10**8, verbose=False):
    s = Sim(tm, size=max(1 << 12, 8 * len(word) + 4096))
    base = s.pos
    for i, c in enumerate(word):
        s.tape[base + 1 + i] = int(c)
    s.hi = base + len(word)
    while s.steps < maxsteps:
        if not s.step():
            return 'HALT', s, None
        if s.state == 0 and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
            w = word_of(s)
            m = parseS(w)
            if verbose: print('   A0 at', s.steps, compress(w))
            if m: return 'S', s, m
    return 'LIMIT', s, None

def word_of(s):
    t = s.tape
    hi = s.hi
    while hi > s.pos and t[hi] == 0: hi -= 1
    return ''.join(map(str, t[s.pos+1:hi+1]))

def parseS(w):
    # w = 1^n (001)^k 000 1^j  (trailing zeros stripped). j may be 0 -> w = 1^n (001)^k (then 000 implicit)
    m = re.match(r'^(1*)((?:001)*)(?:000(1*))?$', w)
    if not m: return None
    n = len(m.group(1)); k = len(m.group(2)) // 3; j = len(m.group(3) or '')
    if m.group(3) is None:
        # no explicit 000 + ones => j = 0
        j = 0
    return (n, k, j)

if __name__ == '__main__':
    j = int(sys.argv[1]); nmax = int(sys.argv[2]); v = len(sys.argv) > 3
    for n in range(1, nmax):
        w = '1' * n + '000' + '1' * j
        r, s, m = run(w, verbose=v)
        print(n, n % 6, r, s.steps, m if r == 'S' else s.show())
