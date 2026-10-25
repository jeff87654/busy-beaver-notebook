from w891 import *
import itertools
s = R['R3Am'][0]
# pass-1 start: stream zeros k+2, blocks k+1+r, d=0
p1 = PS(2, {'k': 1}, 1, {'k': 1, 'r': 1}, 0, {})
grid = [dict(k=k, r=r, y=y) for k, r, y in itertools.product(range(4), range(4), range(3))]
print('start->P1', chk(s, p1, grid))
for vals in grid[:5]:
    print(vals, validate.reaches(s, p1, vals))
