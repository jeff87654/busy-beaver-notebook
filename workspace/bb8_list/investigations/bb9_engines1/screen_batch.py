"""screen_batch.py TAG [--b0 1,3] [--stages 30] [--maxs 3000000] [--src FILE]
Screens the printed renum leaves runs/renum_TAG.tsv (or --src: one machine per line) with mfx.screen at each b0;
appends to runs/mf_TAG.tsv (resumable):  machine  b0:kindA/kindB/stages/cycles/grow/last  ...  zerosA(b0 first)"""
import sys, argparse, time, threading
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
import fam, mfx
ap = argparse.ArgumentParser(); ap.add_argument('tag'); ap.add_argument('--b0', default='1,3')
ap.add_argument('--stages', type=int, default=30); ap.add_argument('--maxs', type=int, default=3_000_000)
ap.add_argument('--src'); ap.add_argument('--out')
a = ap.parse_args()
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl, _, mode = a.tag.partition('_inline')
base, t, n = BASES[lbl][0], BASES[lbl][1], int(BASES[lbl][2])
fam.register(a.tag, base, t, n)
b0s = [int(x) for x in a.b0.split(',')]
for b in b0s:
    if mode:
        fam.inline_start(a.tag, b, mode)
    else:
        fam.start(a.tag, b)
src = a.src or f'runs/renum_{a.tag}.tsv'
out = a.out or f'runs/mf_{a.tag}.tsv'
import os
done = set(l.split('\t')[0] for l in open(out)) if os.path.exists(out) else set()
ms = [l.split()[0] for l in open(src) if l.strip() and not l.startswith('#')]
ms = [m for m in dict.fromkeys(ms) if m not in done]
print(a.tag, len(ms), 'machines', flush=True)
t0 = time.time()
def main():
  with open(out, 'a') as fo:
    for i, m in enumerate(ms):
        cols, za = [m], None
        for b in b0s:
            r = mfx.screen(a.tag, m, a.stages, a.maxs, b0=b)
            last = r['histA'][-1] if r['histA'] else ''
            cols.append(f"b{b}:{r['kind']}/{r.get('kindB','')}/{r['stages']}/{r['cycles']}/{r['grow']}/{last[:40]}")
            if za is None:
                za = mfx.zs(r['histA'])
        cols.append(','.join(map(str, za)))
        fo.write('\t'.join(cols) + '\n'); fo.flush()
th = threading.Thread(target=main); th.start(); th.join()
print('done', len(ms), f'{time.time() - t0:.0f}s', flush=True)
