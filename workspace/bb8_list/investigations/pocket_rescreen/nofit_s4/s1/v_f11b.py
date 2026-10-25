import sys
from val import *
m = sys.argv[1] if len(sys.argv)>1 else '1RB0RE_1RC0RA_0LD0RH_1LA0LE_1RF0RB_0LG---_0LC1LG_1LD0LE'
bad=0; n=0
for y in (2,3,4,5,8,13,40,101):
    for k in range(0,15):
        T = '010001' + '0010'*3 + '0100010'*k + '010001'
        R = '0' + '0001'*3 + '0010'*y + T
        got = bounce_round(m, 'E', R, '0001', '0010')
        exp = (3, 2*y-1, '010001' + '0010'*3 + '0100010'*(k+1) + '010001')
        n+=1
        if got != exp:
            bad+=1
            if bad<6: print('MISMATCH', y, k, got[:2], (got[2][:80] if len(got)>2 else ''))
print(n, 'cases', bad, 'bad')
