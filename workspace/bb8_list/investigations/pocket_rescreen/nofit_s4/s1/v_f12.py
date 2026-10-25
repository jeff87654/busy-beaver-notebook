import sys
from val import *
m = sys.argv[1]
P = lambda y, n: '00' + '1'*y + '0' + '1011'*n + '11'
Qc = lambda x, n: '0' + '1'*x + '0111' + '0' + '1101'*n + '111'
S = lambda N: '0110111' + '0111'*N + '1'
br = lambda R: bounce_round(m, 'C', R, '1', '1', mid='0')
bad = n = 0
def ck(got, exp, tag):
    global bad, n
    n += 1
    if got != exp:
        bad += 1
        if bad < 8: print('MISMATCH', tag, 'got', str(got)[:90], 'exp', str(exp)[:90])
for y in (4, 6, 12, 30, 62, 100):
    for k in range(2, 12):
        ck(br(P(y, k)), (2*y, 3, '0' + '1101'*(k-1) + '111'), f'P{y},{k}')
        ck(br(Qc(2*y, k)), (0, 2*y+18, '0' + '1011'*(k-2) + '11'), f'Q{2*y},{k}')
    ck(br(Qc(2*y, 1)), (2*y+12, 2, ''), f'Qend{2*y}')
    ck(br('0' + '1'*(2*y+12) + '011'), (2, 3, '0111'*((2*y+12)//4) + '1'), f'Z{2*y+12}')
for N in range(3, 40, 3):
    ck(br(S(N)), (0, 12, '0' + '1011'*(N-1) + '11'), f'S{N}')
print(m, n, 'cases', bad, 'bad')
