from lib import *
# first uses of each transition, M10 vs R8, from blank
for name, m in (('M10', M10), ('R8', R8)):
    for tr in ['G0', 'E0', 'I0', 'I1', 'J0', 'J1']:
        if name == 'R8' and tr[0] in 'IJ': continue
        snaps, end = run(m, '', 'A', '', 200000, ['snapany=' + tr, 'maxsnap=1'])
        print(name, tr, snaps[0][0] if snaps else None, end[0], end[1])
snaps, end = run(M10, '', 'A', '', 2000000, ['stop=E0'])
print(end[0], end[1], rle(end[2]), '|', end[3], '|', rle(end[4]))
