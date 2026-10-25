"""Concrete (numeric) accelerated run from beta(1021,0,6,0) using only crossing +
the bounce lemma L0*; confirms the super-step formula without using R1/T1/R2/T2.
Prints every beta(x,0,k,t) configuration reached."""
from symsim import *
L0s = Lemma('L0*', '[A0] 0 (100)^{j} 1010 (110)^{k}', '[A0] 0 (100)^{j+2k} 1010', {'j': 0, 'k': 1}, walled=(False, False))
# note: walled=(False,False) here only requires blank left; right context is not touched (L0 proven right-walled)
L0s.walled = (False, True)
def beta(x, j, k, t):
    return f'[A0] 0 (100)^{x} 1010 (100)^{j} 1010 (110)^{k} 10100 (10)^{t} 1101'
c = make_config(beta(1021, 0, 6, 0))
x, k, t = 1021, 6, 0
seen = 0
for it in range(200000):
    if not L0s.apply(c):
        c.step(); c.normalize()
    # detect beta(x,0,k,t) with j = 0
    if c.state == 0 and c.cell == 0 and not c.left and getattr(c, 'lemma_log', None):
        r = c.right
        if (len(r) >= 3 and r[0] == ('L', '0') and r[1][0] == 'R' and r[1][1] == '100' and r[2][0] == 'L' and r[2][1].startswith('10101010')):
            X = r[1][2].c
            print('beta-like config: x =', X if X < 10**12 else f'2^{(X+3).bit_length()-1} - 3 (exact: {X + 3 == 1 << ((X+3).bit_length()-1)})', ' rest:', ' '.join(t[1] if t[0]=='L' else f'({t[1]})^{t[2]}' for t in r[2:]))
            seen += 1
            if seen >= 3:
                break
