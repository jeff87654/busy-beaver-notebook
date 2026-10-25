"""branch.py: follower-level TNF branching (family GH): for each parent (machine, slot) set the undefined slot to each of
the 40 values, follow with mf35g.follow (real start b0 = 6) for ST stages; children that halt at another undefined I/J
slot at stage >= MINST are branched again (up to LEVELS levels).
usage: python branch.py PARENTS.tsv OUT.tsv [ST=30] [MAXS=3e7] [MINST=2] [LEVELS=2]"""
import sys, re, threading
from pathlib import Path
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35, mf35g
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
src, out = sys.argv[1], Path(sys.argv[2])
ST = int(sys.argv[3]) if len(sys.argv) > 3 else 30
MS = int(float(sys.argv[4])) if len(sys.argv) > 4 else 30_000_000
MINST = int(sys.argv[5]) if len(sys.argv) > 5 else 2
LEVELS = int(sys.argv[6]) if len(sys.argv) > 6 else 2
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1','J0','J1']
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHIJ']
def setslot(m, slot, val):
    i = SL.index(slot); q, c = divmod(i, 2)
    parts = m.split('_'); s = parts[q]
    parts[q] = s[:3 * c] + val + s[3 * c + 3:]
    return '_'.join(parts)
def halt_slot(hist):
    h = hist[-1]
    mm = re.match(r'H (\w)(\d)', h)
    return (mm.group(1) + mm.group(2)) if mm else None
def undefined(m, slot):
    i = SL.index(slot); q, c = divmod(i, 2)
    return m.split('_')[q][3 * c:3 * c + 3] == '---'
done = set(l.split('\t')[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
todo = [(l.split('\t')[0], l.split('\t')[1].strip()) for l in open(src) if l.strip()]
def main():
    global todo
    level = 0
    with out.open('a') as f:
        while todo and level < LEVELS:
            level += 1
            kids = [setslot(m, s, v) for m, s in todo for v in OPTS]
            kids = [k for k in kids if k not in done]
            print('level', level, len(kids), 'children', flush=True)
            nxt = []
            for k in kids:
                try:
                    kind, hist = mf35g.follow('GH', k, ST, MS)
                except Exception as ex:
                    kind, hist = 'CRASH', [repr(ex)[:200]]
                done.add(k)
                f.write('\t'.join([k, kind, str(len(hist)), str(mf35.big_jumps(hist)), ' ; '.join(hist)]) + f'\tL{level}\n'); f.flush()
                if kind == 'HALT' and len(hist) - 1 >= MINST:
                    s = halt_slot(hist)
                    if s and s[0] in 'IJ' and undefined(k, s):
                        nxt.append((k, s))
            todo = nxt
    print('done', flush=True)
t = threading.Thread(target=main); t.start(); t.join()
