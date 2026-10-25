import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ['PATH']
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES, T
import kl

CLS53 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\cls53.txt'
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53'

entries = []
with open(CLS53, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('== '):
            parts = line.split()
            entries.append((parts[1], parts[2], ' '.join(parts[3:])))

with open(os.path.join(OUT_DIR, 'blank_traces_53.txt'), 'w', encoding='utf-8') as out_f:
    for idx, (tag, tm, eb) in enumerate(entries):
        ev = kl.blank(tm, 2000000, maxl=30, T=T(tag))
        out_f.write(f"=== #{idx:02d} [{tag}] {tm} ({eb}) ===\n")
        for e in ev:
            if e[0] == 'K':
                ds_s = ','.join(map(str, e[2])) if len(e[2]) <= 12 else (','.join(map(str, e[2][:4])) + f'..(len={len(e[2])})..' + ','.join(map(str, e[2][-4:])))
                out_f.write(f"  st={e[1]} K([{ds_s}]; a={e[3]}; b={e[4]})\n")
            else:
                out_f.write(f"  {e}\n")
print("Done!")
