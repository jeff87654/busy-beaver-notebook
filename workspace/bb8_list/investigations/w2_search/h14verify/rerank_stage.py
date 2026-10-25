"""python rerank_stage.py PKL STAGE ORDER(comma atom names, low->high)  - re-run one literal stage with given atom order"""
import sys, os, pickle
import vals, absim
from absim import *
d = pickle.load(open(sys.argv[1], 'rb'))
vals.ATOMS.clear(); vals.ATOMS.update(d['ATOMS']); vals._next[0] = max(d['ATOMS']) + 1
runs = d['TRAJ'][int(sys.argv[2]) - 1]
nxt = d['TRAJ'][int(sys.argv[2])] if int(sys.argv[2]) < len(d['TRAJ']) else None
for i, nm in enumerate(sys.argv[3].split(',')):
    a = [x for x in ATOMS if ATOMS[x]['name'] == nm][0]
    ATOMS[a]['rank'] = 5000 + i
print('in :', show(runs)[:400])
print('order:', [(ATOMS[a]['name']) for a in atoms_of(runs)])
kind, out, info = literal_stage(runs, ntr=2, seed=3)
print('out:', kind, show(out)[:400] if out else None)
print('rec:', show(nxt)[:400] if nxt else None)
print('SAME' if out is not None and nxt is not None and show(out) == show(nxt) else 'CHECK')
