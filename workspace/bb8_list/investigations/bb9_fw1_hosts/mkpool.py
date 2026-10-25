"""mkpool.py: collect dlscan3 LOOPER/REBUILD/MULTI/MULTI? rows (7/8/9 states) -> pool.tsv (machine nst src grade template)."""
import idle, os
B = r'C:\Users\jeffr\Downloads\bb8'
SRC = [('dl3_hits', B + r'\bb7_holdouts\dl3_hits\out.tsv'), ('dl3_triage7', B + r'\bb7_holdouts\dl3_triage7\out.tsv'),
       ('pbarrier7', B + r'\bb8_list\investigations\bb9_pbarrier_fw1\candidates_7state.tsv'),
       ('triage7_1RB1LA', B + r'\bb8_list\investigations\bb9_triage7_and_1RB1LA\new_dl3_out.tsv'),
       ('parents', B + r'\bb8_list\investigations\bb9_quickcheck\parents_dl3.tsv'),
       ('bb8_sample', B + r'\bb8_list\investigations\nested_detector\scans\bb8_sample\dl2fits27_dl3.tsv'),
       ('calib', B + r'\bb8_list\investigations\nested_detector\calib_2e7.tsv'),
       ('roots9', B + r'\bb8_list\investigations\bb9_quickcheck\roots9_dl3\merged.tsv'),
       ('c7m12', B + r'\bb8_list\investigations\nested_detector\scans\c7m12\merged.tsv'),
       ('n1f0', B + r'\bb8_list\investigations\nested_detector\scans\n1f0\merged.tsv'),
       ('n1f0c', B + r'\bb8_list\investigations\bb9_n1f0_complete\comp_T_all_dl3.tsv')]
seen = {}
for tag, f in SRC:
    for l in open(f, errors='ignore'):
        x = l.rstrip('\n').split('\t')
        if len(x) < 5 or x[3] not in ('LOOPER', 'REBUILD', 'MULTI', 'MULTI?'): continue
        m = x[0]; ns = (len(m) + 1) // 7
        if ns > 9 or m in seen: continue
        seen[m] = (m, str(ns), tag, x[3], x[4])
with open('pool.tsv', 'w', newline='\n') as f:
    for v in seen.values(): f.write('\t'.join(v) + '\n')
import collections
print(collections.Counter((v[1], v[2], v[3]) for v in seen.values()))
print(len(seen))
