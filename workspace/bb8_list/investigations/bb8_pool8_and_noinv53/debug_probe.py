import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES

p7 = {l.split('\t')[0]: l.strip() for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\pool7.tsv')}
out = {l.split('\t')[0]: l.strip() for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv')}
for k, v in sorted(BASES.items()):
    print(f"{k}: pool7={p7.get(v[0], 'NONE')} | out={out.get(v[0], 'NONE')}")
