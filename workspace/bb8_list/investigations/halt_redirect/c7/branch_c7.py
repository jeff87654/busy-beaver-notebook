"""branch_c7.py: follower-level TNF branching (family C7, 9 states): for each parent machine that halts in the
mini-follower at an undefined H/I slot AFTER at least MINST jumps (a halt renum cannot see literally), set that slot to
each of the 36 values (A..I) and follow the child (b0 = 6) for ST stages; children halting at another undefined H/I slot
at stage >= MINST are branched again (up to LEVELS levels).  Parents whose halting slot is their LAST undefined slot are
skipped (children could not halt).
usage: python branch_c7.py MF_OUT.tsv... --out OUT.tsv [--st 30] [--maxs 3e7] [--minst 1] [--levels 2] [--b0 6]"""
import sys, re, threading, argparse
from pathlib import Path
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/c7')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import c7fam, mf35, mf35g
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
ap = argparse.ArgumentParser()
ap.add_argument('src', nargs='+'); ap.add_argument('--out', required=True)
ap.add_argument('--st', type=int, default=30); ap.add_argument('--maxs', type=float, default=3e7)
ap.add_argument('--minst', type=int, default=1); ap.add_argument('--levels', type=int, default=2)
ap.add_argument('--b0', type=int, default=6)
a = ap.parse_args()
out = Path(a.out); ST, MS, MINST, LEVELS = a.st, int(a.maxs), a.minst, a.levels
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1']
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHI']
def pad9(m):
    return m if m.count('_') == 8 else m + '_------' * (8 - m.count('_'))
def setslot(m, slot, val):
    i = SL.index(slot); q, c = divmod(i, 2)
    parts = m.split('_'); s = parts[q]
    parts[q] = s[:3 * c] + val + s[3 * c + 3:]
    return '_'.join(parts)
def halt_slot(hist):
    mm = re.match(r'H (\w)(\d)', hist[-1])
    return (mm.group(1) + mm.group(2)) if mm else None
def undefined(m, slot):
    i = SL.index(slot); q, c = divmod(i, 2)
    return m.split('_')[q][3 * c:3 * c + 3] == '---'
def nundef(m):
    return sum(m.split('_')[q][3 * c:3 * c + 3] == '---' for q in range(9) for c in range(2))
done = set(l.split('\t')[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
todo = []
import os
for src in a.src:
    if not os.path.exists(src):
        print('missing source (skipped):', src, flush=True); continue
    for l in open(src):
        f = l.rstrip('\n').split('\t')
        if len(f) < 5 or f[1] != 'HALT': continue
        hist = f[4].split(' ; ')
        if len(hist) - 1 < MINST: continue
        m = pad9(f[0]); s = halt_slot(hist)
        if s and s[0] in 'HI' and undefined(m, s) and nundef(m) >= 2:
            todo.append((m, s))
print('parents', len(todo), flush=True)
def main():
    global todo
    level = 0
    with out.open('a') as f:
        while todo and level < LEVELS:
            level += 1
            kids = list(dict.fromkeys(setslot(m, s, v) for m, s in todo for v in OPTS))
            kids = [k for k in kids if k not in done]
            print('level', level, len(kids), 'children', flush=True)
            nxt = []
            for k in kids:
                try:
                    kind, hist = mf35g.follow('C7', k + '_------', ST, MS, b0=a.b0)
                except Exception as ex:
                    kind, hist = 'CRASH', [repr(ex)[:200]]
                done.add(k)
                f.write('\t'.join([k, kind, str(len(hist)), str(mf35.big_jumps(hist)), ' ; '.join(hist)]) + f'\tL{level}\n'); f.flush()
                if kind == 'HALT' and len(hist) - 1 >= MINST:
                    s = halt_slot(hist)
                    if s and s[0] in 'HI' and undefined(k, s) and nundef(k) >= 2:
                        nxt.append((k, s))
            todo = nxt
    print('done', flush=True)
t = threading.Thread(target=main); t.start(); t.join()
