"""ch_parse.py CS.tsv INDEX.tsv: classify cellscan results for clone variants.
LATERH = does not halt in the first (real first-exhaustion) cell but halts in a later cell
(residue-sensitive: the counting-hook signature).  CHANGED = halts nowhere but some cell
fingerprint differs from its base control.  Prints LATERH rows, a tally, and changed counts
by cloned slot."""
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    try: _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)
    except Exception: pass

import sys, collections
idx = {}
bases = {}
for l in open(sys.argv[2]):
    x = l.rstrip('\n').split('\t')
    idx[x[0]] = x
    if x[2] == 'BASE': bases[int(x[1])] = x[0]
res = {}
for l in open(sys.argv[1]):
    x = l.rstrip('\n').split('\t')
    if len(x) >= 4: res[x[0]] = x
ctrl = {bi: res[m] for bi, m in bases.items() if m in res}
for bi, r in ctrl.items():
    print('CONTROL base', bi, r[1], r[2], r[3][:60], flush=True)
tally = collections.Counter(); changed_by = collections.Counter()
for M, r in res.items():
    x = idx.get(M)
    if x is None or x[2] == 'BASE': continue
    let = r[1]
    if let.startswith('H'):
        tally['HALT0'] += 1
    elif 'H' in let:
        tally['LATERH'] += 1
        print('LATERH', M, let, r[2], 'base', x[1], 'slot', x[2], 'entry', x[3], 'val', x[4], flush=True)
    else:
        cr = ctrl.get(int(x[1]))
        if cr and r[3] != cr[3]:
            tally['CHANGED'] += 1; changed_by[x[2]] += 1
        else:
            tally['SAME'] += 1
print('tally', dict(tally), flush=True)
print('changed by slot', dict(changed_by), flush=True)
