import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import json, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES

bm = {v[0]: k for k, v in BASES.items()}
for fn in glob.glob(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\run_*.jsonl'):
    for l in open(fn, encoding='utf-8'):
        try:
            d = json.loads(l)
            if d.get('machine') in bm:
                tag = bm[d['machine']]
                print(f"Base {tag}: verdict={d.get('verdict')} tmpl={d.get('tmpl')} rules={d.get('rules')}")
        except Exception:
            pass
