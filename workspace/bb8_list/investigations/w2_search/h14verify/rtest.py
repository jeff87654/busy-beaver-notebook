"""Generic test of the decisive post-round stage  P 1 2^10 1^D 0 | A  for D in a chosen residue class.
python rtest.py DRES [maxstages] [prefix]   (D atom: residue DRES mod MB, rank below A; A atom = phi)"""
import sys, os
from absim import *
import absim, drive
dres = int(sys.argv[1]); maxst = int(sys.argv[2]) if len(sys.argv) > 2 else 12
D = new_atom('D', dres, MB, rank=1010, note='list length')
A = new_atom('A', stable_phi(MB), MB, rank=1020, note='acc (U output)')
PRE = {
 '0': [('t', Val(2), Val(3)), ('t', Val(1), Val(1)), ('t', Val(7), Val(1)), ('t', Val(0), Val(1)), ('t', Val(5), Val(1)), ('t', Val(1), Val(1))],
 '1': [('t', Val(4), Val(1)), ('t', Val(0), Val(2)), ('t', Val(2), Val(9)), ('t', Val(3), Val(1)), ('t', Val(1), Val(1))],
 '2': [('t', Val(2), Val(1)), ('t', Val(91), Val(1)), ('t', Val(1), Val(1)), ('t', Val(2), Val(6)), ('t', Val(1), Val(1)), ('t', Val(44), Val(1)), ('t', Val(48), Val(1)), ('t', Val(61), Val(1)), ('t', Val(0), Val(1)), ('t', Val(26), Val(1)), ('t', Val(1), Val(1))],
}
pre = PRE[os.environ.get('PREFIX', '0')]
runs = norm(pre + [('t', Val(2), Val(10)), ('t', Val(1), D), ('t', Val(0), Val(1)), ('t', A, Val(1))])
print('D mod 25 =', dres % 25, ' start', show(runs), flush=True)
import pickle
try:
    r = drive.drive(runs, maxst, lambda s: print(s[:600], flush=True))
finally:
    pickle.dump(dict(TRAJ=drive.TRAJ, ATOMS=ATOMS), open(os.environ.get('PKL', 'rtest_traj.pkl'), 'wb'))
print('END', r[0])
if r[0] == 'HALT':
    def ones(rs):
        tot = Val(0)
        for x in rs:
            if x[0] == 't':
                v, c = Val.of(x[1]), Val.of(x[2])
                tot = tot + ((v + 1) * c.c if not c.huge() else c * (v.ival() + 1))
            elif x[0] == 'R':
                b = ones(list(x[1])); assert b.isconst()
                tot = tot + Val.of(x[2]) * b.c
        return tot
    print('ONES at halt (generic part, prefix excluded) =', ones(r[2]) - ones(pre))
    for a, v in ATOMS.items():
        print('  atom', v['name'], 'rank', v['rank'], v['note'][:90])
