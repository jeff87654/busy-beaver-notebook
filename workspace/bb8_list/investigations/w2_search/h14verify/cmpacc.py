import sys, pickle, time, subprocess, os
import vals, absim
from absim import *
d = pickle.load(open('traj.pkl', 'rb')); vals.ATOMS.update(d['ATOMS']); vals._next[0] = max(d['ATOMS']) + 1
TR = d['TRAJ']
def runexe(exe, tape):
    p = subprocess.run([exe], input='%s H %d %d %s\n' % (absim.H14, len(tape), 10**11, tape), capture_output=True, text=True)
    return p.stdout.split()
idx = [int(x) for x in sys.argv[1:]] or range(len(TR))
for i in [x - 1 for x in idx]:
    runs = TR[i]
    if not is_bform(runs): continue
    c = clr(runs)
    if c and c[0] == 'clr': continue
    atoms = atoms_of(runs); rp = rep_sets(atoms, 0)[0]
    tape = render(runs, rp)
    t0 = time.time(); a = runexe('./stage2.exe', tape); t1 = time.time()
    b = runexe('./stage.exe', tape) if len(sys.argv) > 1 or len(tape) < 40000 else None; t2 = time.time()
    same = b is None or a == b
    print(i + 1, 'len', len(tape), 'acc %.2fs' % (t1 - t0), 'plain %.2fs' % (t2 - t1), 'steps', a[1], 'SAME' if same else 'DIFF', a[0], flush=True)
