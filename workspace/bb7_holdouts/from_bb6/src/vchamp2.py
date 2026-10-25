import sys; sys.path.insert(0, '.')
from tm import *
from vchamp import S1
M = parse('1RB1RA_1RC1RZ_1LD0RF_1RA0LE_0LD1RC_1RA0RE')
L, R = S1(3, 7, 2, 6, 63); print(L + '|' + R, len(L + R))
seen = 0
def stop(T, p, q, t, lo, hi, off):
    global seen
    if T[p+1]==0 and T[p+2]==1 and T[p+3]==1 and T[p+4]==1 and T[p+5]==0 and T[p+6]==0 and T[p+7]==1:
        a = lo
        while T[a] == 0: a += 1
        b = hi
        while T[b] == 0: b -= 1
        if b - a > 200 and seen < 3:
            seen += 1; print(t, show(T, p, q, lo, hi))
    return False
run(M, maxsteps=3*10**6, stop=stop)
