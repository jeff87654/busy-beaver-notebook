import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os, subprocess
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ['PATH']
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES, T, targs, word

CLS53 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\cls53.txt'
KMAP2 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\kmap2.exe'
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53'

entries = []
with open(CLS53, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('== '):
            parts = line.split()
            entries.append((parts[1], parts[2], ' '.join(parts[3:])))

# Test configs (ds, a) at b = B0:
# 1. Non-zero bottom digit: ([2, 3], a) for a = 1..8
# 2. Borrow k=1: ([2, 2, 0], a) for a = 3..10
# 3. Borrow k=2: ([2, 2, 0, 0], a) for a = 5..12
# 4. Borrow k=3: ([2, 2, 0, 0, 0], a) for a = 7..14
test_cfgs = []
for a in range(1, 9):
    test_cfgs.append(('D', 0, [2, 3], a))
for k in (1, 2, 3, 4):
    for a in range(2*k + 1, 2*k + 9):
        test_cfgs.append(('B', k, [2, 2] + [0]*k, a))

by_tag = {}
for idx, (tag, tm, eb) in enumerate(entries):
    by_tag.setdefault(tag, []).append((idx, tm, eb))

results = {}
for tag, mlist in sorted(by_tag.items()):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(OUT_DIR, f'tmp_starts_{tag}.txt')
    with open(sf, 'w') as f:
        for i, (kind, k, ds, a) in enumerate(test_cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(OUT_DIR, f'tmp_m_{tag}.txt')
    with open(mf, 'w') as f:
        for idx, tm, eb in mlist:
            f.write(tm + '\n')
    p = subprocess.run([KMAP2, mf] + targs(tag) + [sf, '200000', str(B0)],
                       capture_output=True, text=True, creationflags=0x40)
    for (idx, tm, eb), line in zip(mlist, p.stdout.splitlines()):
        cols = line.split('\t')[1:]
        results[idx] = (tag, tm, eb, cols)

# Print summary of what each of the 53 machines does on D and B1..B4!
with open(os.path.join(OUT_DIR, 'inspect_53.txt'), 'w', encoding='utf-8') as out_f:
    for idx in sorted(results):
        tag, tm, eb, cols = results[idx]
        d_outs = cols[:8]
        b1_outs = cols[8:16]
        b2_outs = cols[16:24]
        b3_outs = cols[24:32]
        b4_outs = cols[32:40]
        out_f.write(f"#{idx:02d} [{tag}] {tm} ({eb})\n")
        out_f.write(f"  D([2,3], a=1..8):  {'  '.join(d_outs)}\n")
        out_f.write(f"  B1([2,2,0], a=3..10): {'  '.join(b1_outs[:6])}\n")
        out_f.write(f"  B2([2,2,0,0], a=5..12): {'  '.join(b2_outs[:6])}\n")
        out_f.write(f"  B3([2,2,0^3], a=7..14): {'  '.join(b3_outs[:6])}\n")
        out_f.write(f"  B4([2,2,0^4], a=9..16): {'  '.join(b4_outs[:6])}\n")

