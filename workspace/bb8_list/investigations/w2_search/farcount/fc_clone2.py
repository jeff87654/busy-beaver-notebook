"""fc_clone2.py: second clone-split (state N) on top of fc_clone's looping DROP1R machines.
Bases are parsed from fc_clone.log (13-state machines that keep six class-12 round starts with
one far eat).  To keep the sweep bounded, bases are selected per first-clone slot by plateau
kD2 (min / median / max).  For each base, for each chosen slot, the slot's target is redirected
to a new state N copying that target's row, and one N entry is varied over all transitions to
A-N plus halt.  Each variant is tracked from the class-12 far start; DROP2 (kD2 decreases at
least twice, counting K -> first RS) and CHANGED (six round starts with a post-first drop) are
printed.  usage: python fc_clone2.py [--log fc_clone.log] [--per 3] [--slots orig,M0,M1]"""
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    try: _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)
    except Exception: pass

import sys, threading, argparse, ast, re
from farfol import track
from fl import far_of, SUF
import mf35

ap = argparse.ArgumentParser(); ap.add_argument('--log', default='fc_clone.log')
ap.add_argument('--per', type=int, default=3); ap.add_argument('--K', type=int, default=29)
ap.add_argument('--slots', default='orig,M0,M1')
a = ap.parse_args()
LET = 'ABCDEFGHIJKLM'
NEW = 'N'

def bases():
    groups = {}
    for l in open(a.log):
        if not l.startswith('DROP1R'): continue
        x = l.split()
        slot, M = x[1], x[4]
        m = re.search(r'kD2 \[([0-9, ]+)\]', l)
        ks = [int(v) for v in m.group(1).split(',')] if m else [0, 0]
        groups.setdefault(slot, []).append((ks[1] if len(ks) > 1 else 0, slot, M))
    out = []
    for slot, v in sorted(groups.items()):
        v.sort()
        picks = {v[0], v[len(v) // 2], v[-1]} if a.per >= 3 else {v[0]}
        out += sorted(picks)
    return out

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

def go():
    w = far_of(a.K) + mf35.word_of_tokens([2, 5] + [1] * 40 + [0, 0, 0, 9] + [1] * 29 + [1, 19]) + SUF
    opts = [w_ + d + q for w_ in '01' for d in 'LR' for q in LET + NEW] + ['---']
    B = bases()
    print('bases', len(B), flush=True)
    for plat, slot1, M in B:
        print('BASE', slot1, 'plateau', plat, M, flush=True)
    n = 0; tally = {}
    for plat, slot1, M in B:
        rows0 = M.split('_')
        slots = []
        for s in a.slots.split(','):
            slots.append(slot1 if s == 'orig' else s)
        for slot in slots:
            for entry in (0, 1):
                for val in opts:
                    M2 = build(rows0, slot, entry, val)
                    if M2 is None: continue
                    n += 1
                    try:
                        o = track(M2, nrs=6, maxst=200, maxs=10**8, start=w)
                    except Exception as ex:
                        print('ERR', slot, entry, val, str(ex)[:60], flush=True); continue
                    ks = [a.K] + [kd for _, kd, _, _, _, _, _ in o['rs']]
                    cs = [c % 14 for _, _, _, _, c, _, _ in o['rs']]
                    drops = sum(1 for i in range(len(ks) - 1) if ks[i + 1] < ks[i])
                    key = (o['end'], drops, len(o['rs']))
                    tally[key] = tally.get(key, 0) + 1
                    if drops >= 2:
                        print('DROP2', slot1, slot, entry, val, M2, 'kD2', ks, 'cls', cs, o['end'], o['slot'], flush=True)
        print('base done', slot1, plat, 'tried', n, 'tally', tally, flush=True)
    print('DONE', n, tally, flush=True)

threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
