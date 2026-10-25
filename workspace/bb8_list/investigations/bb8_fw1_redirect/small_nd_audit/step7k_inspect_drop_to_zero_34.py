import os
from step7j_analyze_groups_399 import std_399, unusual, bdet

print(f"Total unusual entries: {len(unusual)}")
unusual_ms = set(u[1] for u in unusual)
print(f"Unique machines with unusual B/LB entries: {len(unusual_ms)}")

for r in std_399:
    if r["m"] in unusual_ms:
        bd = r["bdet"]
        ep = "".join(r["E"][a][0] for a in range(1, 17))
        e1_6 = [f"{a}:{r['E'][a][4]};{r['E'][a][2]}" if r["E"][a][0]=="K" else f"{a}:{r['E'][a][0]}" for a in range(1, 7)]
        print(f"=== [{r['tag']}] {r['m']} E={ep} {e1_6} ===")
        print(f"  Blank: st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}' first='{bd['first_ks']}'")
        for k in (1, 2, 3):
            print(f"  B{k}: odd={r['fit_B'][k][1]} | even={r['fit_B'][k][0]}")
            print(f"  LB{k}: odd={r['fit_LB'][k][1]} | even={r['fit_LB'][k][0]}")
