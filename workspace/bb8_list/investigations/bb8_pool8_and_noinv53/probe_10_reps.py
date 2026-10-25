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

# Representatives of the 9 unsettled Ackermann groups:
# A1: #04 (and #11, #23, #25)
# A2: #06 (and #07, #08, #13, #14, #24, #27, #28)
# B:  #17 (and #18..#21, #31..#35, #40..#42, #44, #45)
# C:  #03
# D:  #05 (and #12, #26)
# E:  #09 (and #29)
# F:  #10 (and #30)
# G:  #36 (and #37, #46, #47)
# H:  #38 (and #48)
# I:  #39 (and #49)
reps = [3, 4, 5, 6, 9, 10, 17, 36, 38, 39]

# Probe k = 1..8 at two values of a (e.g. a = 2*k+5 and 2*k+7, plus even a = 2*k+6 and 2*k+8 for #17)
test_cfgs = []
for a in range(1, 7):
    test_cfgs.append(('D', 0, [2, 3], a))
for k in range(1, 9):
    for a in (2*k + 3, 2*k + 4, 2*k + 5, 2*k + 6):
        test_cfgs.append(('B', k, [2, 2] + [0]*k, a))
for A in range(1, 13):
    test_cfgs.append(('E', A, [], A))

with open(os.path.join(OUT_DIR, 'reps_rules.txt'), 'w', encoding='utf-8') as out_f:
    for idx in reps:
        tag, tm, eb = entries[idx]
        B0 = BASES[tag][2]
        tt = T(tag)
        sf = os.path.join(OUT_DIR, f'tmp_rep_starts_{idx}.txt')
        with open(sf, 'w') as f:
            for i, (kind, k, ds, a) in enumerate(test_cfgs):
                w = word(tag, ds, a, B0)
                f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
        mf = os.path.join(OUT_DIR, f'tmp_rep_m_{idx}.txt')
        with open(mf, 'w') as f:
            f.write(tm + '\n')
        p = subprocess.run([KMAP2, mf] + targs(tag) + [sf, '300000', str(B0)],
                           capture_output=True, text=True, creationflags=0x40)
        cols = p.stdout.splitlines()[0].split('\t')[1:]
        out_f.write(f"=== REP #{idx:02d} [{tag}] {tm} ({eb}) B0={B0} ===\n")
        out_f.write("  D([2,3], a=1..6): " + "  ".join(f"a={a}:{cols[a-1]}" for a in range(1, 7)) + "\n")
        pos = 6
        for k in range(1, 9):
            s = "  ".join(f"a={2*k+3+j}:{cols[pos+j]}" for j in range(4))
            out_f.write(f"  B{k}([2,2,0^{k}]): {s}\n")
            pos += 4
        e_str = "  ".join(f"A={A}:{cols[pos+A-1]}" for A in range(1, 13))
        out_f.write(f"  E(A=1..12): {e_str}\n\n")
print("Done!")
