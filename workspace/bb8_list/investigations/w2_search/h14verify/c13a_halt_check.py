"""Re-run C13a's halting stage (last config of c13a_traj.pkl) under different magnitude orders of the constant-tier atoms."""
import sys, os, pickle
import vals, absim
from absim import *
d = pickle.load(open('c13a_traj.pkl', 'rb'))
vals.ATOMS.clear(); vals.ATOMS.update(d['ATOMS']); vals._next[0] = max(d['ATOMS']) + 1
runs = d['TRAJ'][-1]
ats = atoms_of(runs)
print('config:', show(runs, 80)[:900])
for a in ats:
    print('  ', ATOMS[a]['name'], ATOMS[a].get('tier'), ATOMS[a]['rank'], ATOMS[a]['note'][:80])
byname = {ATOMS[a]['name'].split('#')[0] + '#' + ATOMS[a]['name'].split('#')[1]: a for a in ats}
order = os.environ.get('ORDER', '')
if order:
    for i, nm in enumerate(order.split(',')):
        a = [x for x in ats if ATOMS[x]['name'] == nm][0]
        ATOMS[a]['rank'] = 500 + i
print('ranks now:', [(ATOMS[a]['name'], ATOMS[a]['rank']) for a in sorted(ats, key=lambda x: ATOMS[x]['rank'])])
kind, out, info = literal_stage(runs, ntr=3, seed=11)
print('RESULT', kind, info.get('q'), info.get('sym'), info['steps'])
