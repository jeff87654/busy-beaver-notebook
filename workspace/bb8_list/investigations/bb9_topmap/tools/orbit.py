import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import idle
"""orbit.py RULES K0A K0B [MAXN]: real top-level orbit in p-adic arithmetic with B = R = R_* (stable tower residue).
RULES: 'M:r=a,b,c,d;r=a,b,c,d;r=exit;...' : for K = r mod M, K' = (a K + b R + c)/d (checked exact); 'exit' or missing r = exit.
K0 = K0A * B + K0B.  Repeats with moduli 5^40, 5^60, 5^80 (x 2^10 3^10) to check stability; prints residues of each top."""
from towres import Rstar
def parse(s):
    M, body = s.split(':', 1); M = int(M); R = {}
    for it in body.split(';'):
        r, v = it.split('='); R[int(r)] = None if v == 'exit' else tuple(int(x) for x in v.split(','))
    return M, R
def orbit(M, RU, K0a, K0b, P, maxn):
    Rs = Rstar(P) % P; K = (K0a * Rs + K0b) % P; out = []; prec = P
    while len(out) < maxn:
        r = K % M; out.append((r, K % 625)); ru = RU.get(r)
        if ru is None: return out, 'exit r=%d' % r
        a, b, c, d = ru; num = a * K + b * Rs + c
        if num % d: return out, 'NONINT'
        K = (num // d) % (prec // d); prec //= d
        if prec < M * 25: return out, 'PRECISION'
    return out, 'MAXN'
if __name__ == '__main__':
    M, RU = parse(sys.argv[1]); K0a, K0b = int(sys.argv[2]), int(sys.argv[3]); maxn = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    for e in (40, 60, 80):
        P = 5 ** e * 2 ** 10 * 3 ** 10
        o, why = orbit(M, RU, K0a, K0b, P, maxn)
        print('5^%d: %d tops (incl. exit top), %s; residues mod %d:' % (e, len(o), why, M), [x[0] for x in o][:60])
