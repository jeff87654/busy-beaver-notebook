import sys, pickle
sys.path.insert(0, 'snap')
import absim, vals
from absim import *
T12 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---'
dd = pickle.load(open(sys.argv[1], 'rb')); idx = int(sys.argv[2])
vals.ATOMS.clear(); vals.ATOMS.update(dd['ATOMS']); vals._next[0] = max(dd['ATOMS']) + 1
runs = dd['TRAJ'][idx - 1]
print('input', show(runs, 80))
atoms = atoms_of(runs); reps = rep_sets(atoms, 2)
absim.RUN = absim.Runner()
for rp in reps:
    tape = render(runs, rp)
    r = absim.RUN.run(T12, 'H', len(tape), tape, 4 * 10**11)
    g = group(tokens(r['word']))
    print({ATOMS[a]['name']: rp[a] for a in atoms}, r['kind'], r['steps'], r['q'], r['sym'])
    print('   ', ' '.join('%s%s' % (x[0], x[1:]) if x[0] != 'R' else 'R[%d]x%d' % (len(x[1]), x[2]) for x in g)[-700:])
