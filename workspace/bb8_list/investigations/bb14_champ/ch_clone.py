"""ch_clone.py BASES.txt OUTPREFIX [--new K]: clone-split generator for champ-family loopers.
For each base (10-state) machine and each defined slot in rows E..J, redirect the slot's target
to a new state copying that target's row, then vary one entry of the copy over all transitions
(targets A..new) plus halt.  Writes OUTPREFIX.txt (variants + the bases as controls, one per
line) and OUTPREFIX_index.tsv (machine, base_idx, slot, entry, value)."""
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    try: _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)
    except Exception: pass

import sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('bases'); ap.add_argument('out')
ap.add_argument('--new', default='K'); ap.add_argument('--rows', default='EFGHIJ')
ap.add_argument('--let', default='ABCDEFGHIJ')
a = ap.parse_args()
NEW = a.new
LET = a.let

def build(rows0, slot, entry, val):
    rows = list(rows0)
    idx = {q: i for i, q in enumerate(LET)}
    si, sy = idx[slot[0]], int(slot[1])
    t = rows[si][3 * sy:3 * sy + 3]
    if t == '---' or t[2] not in idx: return None
    tgtrow = rows[idx[t[2]]]
    nrow = tgtrow[:3 * entry] + val + tgtrow[3 * entry + 3:]
    rows[si] = rows[si][:3 * sy] + t[:2] + NEW + rows[si][3 * sy + 3:]
    rows.append(nrow)
    return '_'.join(rows)

bases = [l.strip() for l in open(a.bases) if l.strip()]
opts = [w + d + q for w in '01' for d in 'LR' for q in LET + NEW] + ['---']
slots = [r + s for r in a.rows for s in '01']
fo = open(a.out + '.txt', 'w'); fi = open(a.out + '_index.tsv', 'w')
n = 0
for bi, M in enumerate(bases):
    fo.write(M + '\n'); fi.write(f'{M}\t{bi}\tBASE\t-\t-\n'); n += 1
    rows0 = M.split('_')
    for slot in slots:
        for entry in (0, 1):
            for val in opts:
                M2 = build(rows0, slot, entry, val)
                if M2 is None: continue
                fo.write(M2 + '\n'); fi.write(f'{M2}\t{bi}\t{slot}\t{entry}\t{val}\n'); n += 1
fo.close(); fi.close()
print('wrote', n, 'machines for', len(bases), 'bases')
