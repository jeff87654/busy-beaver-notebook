"""fc_clone.py: clone-split enumeration around the L12f class-12 looper (12 states).
For each gadget slot (J/K/L rows), redirect its target to a new state M that copies the old
target's row, then vary one entry of M's row over all transitions (plus halt).  Each variant is
tracked from the class-12 far start (far_K + [2 5 1^40 0^3 9 1^29|1|19]); print DROP2 (kD2
decreases at least twice, counting the initial K -> first RS), DROP1R (one drop but >= 3 round
starts all class 12), plus a tally.  usage: python fc_clone.py [--K 29] [--slots J0,K0,..]"""
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    try: _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)
    except Exception: pass

import sys, threading, argparse
from farfol import track
from fl import far_of, SUF
import mf35

L12F = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0LL0RA_1LL0LI'
ap = argparse.ArgumentParser(); ap.add_argument('--K', type=int, default=29)
ap.add_argument('--slots', default='J0,J1,K0,K1,L0,L1'); ap.add_argument('--new', default='M')
a = ap.parse_args()
ROWS = L12F.split('_')
IDX = {q: i for i, q in enumerate('ABCDEFGHIJKL')}
NEW = a.new

def build(slot, entry, val):
    rows = list(ROWS)
    si, sy = IDX[slot[0]], int(slot[1])
    t = rows[si][3 * sy:3 * sy + 3]
    if t == '---': return None
    tgt = t[2]
    mrow = list(rows[IDX[tgt]])          # copy of target row, chars
    m = rows[IDX[tgt]]
    m2 = m[:3 * entry] + val + m[3 * entry + 3:]
    rows[si] = rows[si][:3 * sy] + t[:2] + NEW + rows[si][3 * sy + 3:]
    rows.append(m2)
    return '_'.join(rows)

def go():
    w = far_of(a.K) + mf35.word_of_tokens([2, 5] + [1] * 40 + [0, 0, 0, 9] + [1] * 29 + [1, 19]) + SUF
    tgts = list('ABCDEFGHIJKL') + [NEW]
    opts = [w_ + d + q for w_ in '01' for d in 'LR' for q in tgts] + ['---']
    n = 0; tally = {}
    # control: unmodified L12f
    o = track(L12F, nrs=6, maxst=200, maxs=10**8, start=w)
    print('CONTROL', o['end'], [(kd, c % 14) for _, kd, _, _, c, _, _ in o['rs']], flush=True)
    for slot in a.slots.split(','):
        for entry in (0, 1):
            for val in opts:
                M = build(slot, entry, val)
                if M is None: continue
                n += 1
                try:
                    o = track(M, nrs=6, maxst=200, maxs=10**8, start=w)
                except Exception as ex:
                    print('ERR', slot, entry, val, str(ex)[:60], flush=True); continue
                ks = [a.K] + [kd for _, kd, _, _, _, _, _ in o['rs']]
                cs = [c % 14 for _, _, _, _, c, _, _ in o['rs']]
                drops = sum(1 for i in range(len(ks) - 1) if ks[i + 1] < ks[i])
                key = (o['end'], drops, len(o['rs']))
                tally[key] = tally.get(key, 0) + 1
                if drops >= 2:
                    print('DROP2', slot, entry, val, M, 'kD2', ks, 'cls', cs, o['end'], o['slot'], flush=True)
                elif drops == 1 and len(o['rs']) >= 3 and all(c == 12 for c in cs):
                    print('DROP1R', slot, entry, val, M, 'kD2', ks, 'cls', cs, o['end'], o['slot'], flush=True)
        print('slot', slot, 'done; tried', n, 'tally', sorted(tally.items())[-8:], flush=True)
    print('DONE', n, tally, flush=True)

threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
