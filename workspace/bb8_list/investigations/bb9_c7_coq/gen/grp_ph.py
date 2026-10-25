"""C7 rebuild phases (X'), all E0-free (literal: pkf8 / tools/c7m.exe).  acc = a+5 (= 3R+2), k free.
 PB : Kx(1^n ++ [1]; 1; acc; t; e1) -->+ Kt(1^(K'-1) ++ [7]; 1; 2; t),  n = k+11, K' = 4a+n+17 (= 12R+n+5)
 PD : Kx(1^K; 1; acc; t; 00 D7 D1 e11) -->+ Kx(1^(K-3) ++ [7; 2a+18]; 1; 2; t; D0 e11),  K = k+20  (2a+18 = 6R+12)
 R30: Kx(1^(N+1) ++ [3]; 1; acc; t; D0 e11) -->+ Kx(1^N ++ [2a+13; 0]; 1; 2; t; D0 e11),  N = k+5   (6R+7)
 E2 : Kx(1^N; 1; acc; t; D0 D0 e11) -->+ Kx(1^(N-1) ++ [2a+10]; 1; 2; t; 00 D2 D0 blank),  N = k+6  (6R+4)
 E3 : Kx(1^N; 1; acc; t; 00 D2 D0 blank) -->+ Kx(1^(N-2) ++ [2a+16]; 1; 2; t; blank),  N = k+6   (6R+10)"""
from common import *
from shapes import *
def tl(tc=0):
    return [1, 0, 0, 1] + list(TB) * tc + [run(TB, t=1), 1, 1]
A = accr(5, 'a', (0, 1))
def Zs(c): return list(Z) * c + [run(Z, k=1)]
def tokA(c, coef=2):
    return [1] + [0, 1] * c + [run((0, 1) * coef, a=1)]
E11 = [1, 1, BLANK]; E1 = [1, BLANK]; BL = [BLANK]
def K(acc, rest): return ('B', tl() + acc + tok(1) + rest, [BLANK], '>')
ITEMS = [
 ('PB', K(A, Zs(11) + tok(1) + E1), K(accr(2), Zs(27)[:-1] + [run(Z * 4, a=1), run(Z, k=1)] + tok(7) + E11)),
 ('PD', K(A, Zs(20) + [0, 0] + tok(7) + tok(1) + E11), K(accr(2), Zs(17) + tok(7) + tokA(18) + [1] + E11)),
 ('R30', K(A, Zs(6) + tok(3) + [1] + E11), K(accr(2), Zs(5) + tokA(13) + tok(0) + [1] + E11)),
 ('E2', K(A, Zs(6) + [1, 1] + E11), K(accr(2), Zs(5) + tokA(10) + [0, 0] + tok(2) + tok(0) + BL)),
 ('E3', K(A, Zs(6) + [0, 0] + tok(2) + tok(0) + BL), K(accr(2), Zs(4) + tokA(16) + BL)),
]
ITEMS = [(n, S0, T0, dict(splits=2, maxstages=400), ()) for n, S0, T0 in ITEMS]
import os
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
