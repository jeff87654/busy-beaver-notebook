"""Literal check of the P/Q family rules.
P(N,M) = 0^inf A>0 (abb)^N (bab)^M x 0^inf ;  Q(N,M) = 0^inf A>0 (abb)^N b (bab)^M x 0^inf
with a=10, b=100, x=1.  For each start config, run literally until the next left-edge
state-A config that is a P or Q family member, and compare with the predicted successor."""
import re, sys, json
from tmlib import *

rxP = re.compile(r'^((?:10100100)*)((?:10010100)*)1$')
def classify(bits):
    # P: (abb)^N (bab)^M x ; Q: (abb)^N b (bab)^M x
    m = re.fullmatch(r'((?:10100100)*)((?:10010100)*)1', bits)
    if m: return ('P', len(m.group(1)) // 8, len(m.group(2)) // 8)
    m = re.fullmatch(r'((?:10100100)*)100((?:10010100)*)1', bits)
    if m: return ('Q', len(m.group(1)) // 8, len(m.group(2)) // 8)
    return None

def word(kind, N, M):
    return expand(('abb*%d ' % N if N else '') + ('b ' if kind == 'Q' else '') + ('bab*%d ' % M if M else '') + 'x')

def predict(kind, N, M):
    if kind == 'P':
        return ('Q', 2*N+1, M-1) if M >= 1 else ('Q', 2, N)
    else:
        return ('P', 2*N+2, M-1) if M >= 1 else ('Q', 2, 2*N+1)

def successor(tm, kind, N, M, maxsteps=10**8):
    sim = Sim(tm, word(kind, N, M))
    while True:
        r = run_until_left(sim, maxsteps)
        if r != 'left':
            return (r, sim.steps, None)
        c = classify(sim.word())
        if c:
            return ('ok', sim.steps, c)

if __name__ == '__main__':
    tmname = sys.argv[1] if len(sys.argv) > 1 else 'main'
    tm = {'main': MAIN, 'v1': VAR1, 'v2': VAR2}[tmname]
    Nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    Mmax = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    bad = 0; tot = 0; res = []
    for kind in 'PQ':
        for N in range(0, Nmax + 1):
            for M in range(0, Mmax + 1):
                st, steps, c = successor(tm, kind, N, M)
                p = predict(kind, N, M)
                ok = (st == 'ok' and c == p)
                tot += 1
                if not ok:
                    bad += 1
                    print('MISMATCH', kind, N, M, st, steps, c, 'predicted', p)
                res.append(dict(kind=kind, N=N, M=M, status=st, steps=steps, got=c, pred=p, ok=ok))
    print('%s: %d cases, %d mismatches' % (tmname, tot, bad))
    json.dump(res, open('check_family_%s.json' % tmname, 'w'), indent=0)
