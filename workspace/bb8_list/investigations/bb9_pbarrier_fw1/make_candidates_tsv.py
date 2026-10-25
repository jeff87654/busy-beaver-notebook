import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from pathlib import Path

p1 = Path(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv')
p2 = Path(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv')

by_m = {}
for p in (p1, p2):
    for line in p.read_text().splitlines()[1:]:
        if not line.strip() or line.startswith('#'): continue
        parts = line.split('\t')
        if len(parts) >= 7 and parts[3] in ('MULTI', 'MULTI?', 'REBUILD', 'R4-SOME'):
            by_m[parts[0]] = line

out = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_pbarrier_fw1\candidates_7state.tsv')
out.write_text("machine\thalted_step\tn_templates\tgrade\ttemplate\tw1\tparams\n" + "\n".join(sorted(by_m.values())) + "\n")
print(f"Wrote {len(by_m)} rows to {out}")
