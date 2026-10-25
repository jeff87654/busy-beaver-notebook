"""Start at round 2's end, Per ((4U11-13)/7) 8 n14 a15, with exact high-precision residues and the corrected
magnitude tiers; follow with drive (REATOM)."""
import sys, os, json, pickle
from absim import *
import absim, drive
J = json.load(open('r2end.json'))
U11 = new_atom('U11', J['phi'], MB, rank=1011, note='left-event acc of the restart')
n14 = new_atom('n14', J['n14'], MB, rank=1014, note='depth after round 2')
a15 = new_atom('a15', J['phi'], MB, rank=1015, note='acc after round 2', geU=n14)
for a in ATOMS.values(): a['tier'] = 'real'
k2 = (U11 * 4 - 13).div(7)
runs = norm([('t', Val(2), k2), ('t', Val(5), Val(1)), ('t', Val(1), Val(8)), ('t', Val(0), Val(2)), ('t', Val(2), Val(1)),
             ('t', Val(1), n14), ('t', Val(0), Val(1)), ('t', a15, Val(1))])
print('start', show(runs), flush=True)
try:
    r = drive.drive(runs, int(sys.argv[1]) if len(sys.argv) > 1 else 200, lambda s: print(s[:700], flush=True))
    print('END', r[0])
finally:
    pickle.dump(dict(TRAJ=drive.TRAJ, ATOMS=ATOMS), open('r2end_traj.pkl', 'wb'))
