"""mkstarts.py TEMPLATE K B1,B2,.. : renum start lines for the exhausted configuration K(0^K; 0; b) of a dlscan3
template (O = R): P (u^be s)^K u^be s u^(alB b + beB) S, head on the blank right of it, state Q."""
import sys, re
t, K, Bs = sys.argv[1], int(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')]
f = t.split(','); Q = f[1]; P = f[2][2:].replace('-', ''); u = f[3][2:]; s = f[4][2:]
al, be = map(int, re.match(r'd=(\d+)d\+(\d+)', f[5]).groups()); alB, beB = map(int, re.match(r'b=(\d+)b\+(\d+)', f[6]).groups())
S = f[7][2:].replace('-', '')
for b in Bs:
    w = P + (u * be + s) * (K + 1) + u * (alB * b + beB) + S
    print(f'K{K}_b{b} {w} {len(w)} {Q}')
