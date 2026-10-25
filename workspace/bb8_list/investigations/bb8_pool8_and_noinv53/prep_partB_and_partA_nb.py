import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES

OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53'
CLS53 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\cls53.txt'
p7 = {l.split('\t')[0]: l.split('\t')[1] for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\pool7.tsv') if '\t' in l}

entries = []
with open(CLS53, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('== '):
            parts = line.split()
            tag, tm = parts[1], parts[2]
            eb_info = ' '.join(parts[3:])
            base_tm = BASES[tag][0]
            tpl = p7[base_tm]
            entries.append((tag, tm, tpl, eb_info))

print(f"Parsed {len(entries)} machines from cls53.txt")
pool_path = os.path.join(OUT_DIR, 'pool_noinv53.tsv')
with open(pool_path, 'w', encoding='utf-8') as f:
    for tag, tm, tpl, eb_info in entries:
        f.write(f"{tm}\t{tpl}\t99\t99\t0\t{tag}\n")

for fn in ['run_noinv53_0.jsonl', 'run_noinv53_1.jsonl']:
    fp = os.path.join(OUT_DIR, fn)
    if os.path.exists(fp):
        os.remove(fp)
print(f"Wrote {pool_path} and cleaned old jsonl files")
