"""cr.py MACHINE K DUMP MAXMACRO PE NPFX [edits] : ms.exe from dump with edits; print when the first NPFX tokens
(far-left structure, compressed) change; shows acc (largest run) too. Edits as msrun: IDX=VAL."""
import re, subprocess, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
m, K, dump, mm, pe, npf = sys.argv[1:7]; npf = int(npf)
line = open(dump).read().splitlines()[1]; head, toks = line.split('|', 1); toks = toks.split()
SAVE=[a for a in sys.argv[7:] if a.startswith('--save=')]
SAVE=(SAVE[0][7:].split(',')[0], int(SAVE[0][7:].split(',')[1])) if SAVE else None
for e in [a for a in sys.argv[7:] if not a.startswith('--')]:
    k, v = e.split('='); i = int(k); b = toks[i].split('^')[0]; toks[i] = f'{b}^{v}'
ms = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p = subprocess.Popen([ms, m, K, mm, 'p' + pe, 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\pids.txt', 'a').write(f'{p.pid}\tgroupE1\tms {K} {mm}\n')
p.stdin.write(head + '| ' + ' '.join(toks) + '\n'); p.stdin.close()
def comp(t):
    t = [x[:-2] if x.endswith('^1') else x for x in t]
    out = []; i = 0; n = len(t)
    while i < n:
        best = (1, 1)
        for p in range(1, 13):
            r = 1
            while i + (r + 1) * p <= n and t[i + r * p:i + (r + 1) * p] == t[i:i + p]: r += 1
            if r >= 3 and r * p > best[0] * best[1]: best = (p, r)
        p, r = best
        if r >= 3: out.append('(' + ' '.join(t[i:i + p]) + ')x%d' % r); i += p * r
        else: out.append(t[i]); i += 1
    return ' '.join(out)
prev = None; last = None
for l in p.stdout:
    l = l.rstrip('\n')
    if l.startswith('T ') and SAVE and int(l.split()[1]) >= SAVE[1]:
        open(SAVE[0],'w').write('DUMP '+l.split()[1]+chr(10)+l.split(None,3)[3]+chr(10)); SAVE=None
    if l.startswith('T '):
        a, b = l.split('|', 1); ts = b.replace('[', '').replace(']', '').split()
        side = 'R' if b.strip().endswith(']') else 'L'
        if side == 'L': ts = ts[::-1]  # keep far-left first convention? (tape order already left->right)
        ts = b.replace('[', '').replace(']', '').split()
        key = comp(ts[:npf]) if npf > 0 else comp(ts[npf:])
        mx = max((int(t.split('^')[1]) if '^' in t else 1) for t in ts)
        if key != prev:
            print(a.split()[1], a.split()[2], 'max=%d' % mx, '|', comp(ts)[:260]); prev = key
        last = (a, mx, ts)
    else: print(l)
if last: print('LAST', last[0].split()[1], last[0].split()[2], 'max=%d' % last[1], '|', comp(last[2])[:400])
