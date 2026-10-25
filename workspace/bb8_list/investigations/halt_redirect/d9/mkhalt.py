"""Literal halting configurations of the D9 machine (state I on a 0) for representatives (A, r).
Closed form checked against grid2 dumps: L = tok(A) (10)^7 1 1 0 1 0 1, head on 0, R = 0 1 1 tok-ish (10)^(2r+5) 0 1 0 1 1 0 1 1 1 (10)^9 1 1 0 1 1 0 1 1 0 1"""
import sys
def halt_word(A, r):
    L = '10'*A + '1' + '10'*7 + '110101'
    R = '011' + '10'*(2*r+5) + '010110111' + '10'*9 + '1101101101'
    return L + '0' + R, len(L)
if __name__ == '__main__':
    pairs = [tuple(map(int, p.split(':'))) for p in sys.argv[1:]]
    for A, r in pairs:
        w, h = halt_word(A, r)
        print(f'A{A}_r{r} {w} {h} I')
