from lib import *
for tr in ['E0','I0','I1','J1','G0']:
    snaps, end = run(M10, '', 'A', '', 20000, ['snapany=' + tr, 'maxsnap=40'])
    print(tr, [s[0] for s in snaps])
for n in [100, 200, 500, 1000, 3000, 10000, 30000, 100000, 1000000, 10000000]:
    snaps, end = run(M10, '', 'A', '', n)
    print(n, end[0], len(end[2])+len(end[4]), rle(end[2]), '|', end[3], '|', rle(end[4]))
