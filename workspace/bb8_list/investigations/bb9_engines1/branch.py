"""branch.py TAG [--levels 2] : follower-level TNF branching.  For every screened machine of runs/mf_TAG.tsv (and of
earlier branch levels) whose run A (any b0) halts at an undefined slot AFTER >= 1 jump, while the machine has >= 2
undefined slots, set that slot to each value (write, move, target A..I; 36 values) and screen the children
(same b0s/stages).  Output runs/mfbr_TAG.tsv (same format + level column)."""
import sys, argparse, re, os, time, threading
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
import fam, mfx
ap = argparse.ArgumentParser(); ap.add_argument('tag'); ap.add_argument('--b0', default='1,3')
ap.add_argument('--stages', type=int, default=30); ap.add_argument('--maxs', type=int, default=3_000_000)
ap.add_argument('--levels', type=int, default=2)
a = ap.parse_args()
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl, _, mode = a.tag.partition('_inline')
base, t, n = BASES[lbl][0], BASES[lbl][1], int(BASES[lbl][2])
fam.register(a.tag, base, t, n)
b0s = [int(x) for x in a.b0.split(',')]
for b in b0s:
    fam.inline_start(a.tag, b, mode) if mode else fam.start(a.tag, b)
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHI']
def pad(m): return m + '_------' * (8 - m.count('_'))
def slots(m): return [r[i:i + 3] for r in pad(m).split('_') for i in (0, 3)]
def setslot(m, s, v):
    q, c = 'ABCDEFGHI'.index(s[0]), int(s[1]); rows = pad(m).split('_')
    rows[q] = rows[q][:3 * c] + v + rows[q][3 * c + 3:]; return '_'.join(rows)
def parents(rows):
    out = []
    for f in rows:
        m = f[0]
        for col in f[1:]:
            if not col.startswith('b'): continue
            ka, kb, st, cyc, gr, last = col.split(':', 1)[1].split('/', 5)
            mm = re.match(r'H (\w)(\d)', last)
            if ka == 'HALT' and int(st) >= 1 and mm:
                s = mm.group(1) + mm.group(2)
                sl = slots(m)
                if sl['ABCDEFGHI'.index(s[0]) * 2 + int(s[1])] == '---' and sl.count('---') >= 2:
                    out.append((m, s)); break
    return out
src = [l.rstrip('\n').split('\t') for l in open(f'runs/mf_{a.tag}.tsv')]
outp = f'runs/mfbr_{a.tag}.tsv'
prev = [l.rstrip('\n').split('\t') for l in open(outp)] if os.path.exists(outp) else []
done = set(f[0] for f in prev)
def main():
    todo = parents(src)
    print('level-1 parents', len(todo), flush=True)
    with open(outp, 'a') as fo:
        for lev in range(1, a.levels + 1):
            kids = list(dict.fromkeys(setslot(m, s, v) for m, s in todo for v in OPTS))
            print('level', lev, len(kids), 'children', flush=True)
            rows = []
            for k in kids:
                if k in done:
                    rows += [f for f in prev if f[0] == k]; continue
                cols = [k]; za = None
                for b in b0s:
                    r = mfx.screen(a.tag, k, a.stages, a.maxs, b0=b)
                    last = r['histA'][-1] if r['histA'] else ''
                    cols.append(f"b{b}:{r['kind']}/{r.get('kindB','')}/{r['stages']}/{r['cycles']}/{r['grow']}/{last[:40]}")
                    if za is None: za = mfx.zs(r['histA'])
                cols.append(','.join(map(str, za)))
                fo.write('\t'.join(cols) + f'\tL{lev}\n'); fo.flush(); done.add(k); rows.append(cols)
            todo = parents(rows)
            if not todo: break
th = threading.Thread(target=main); th.start(); th.join(); print('done', flush=True)
