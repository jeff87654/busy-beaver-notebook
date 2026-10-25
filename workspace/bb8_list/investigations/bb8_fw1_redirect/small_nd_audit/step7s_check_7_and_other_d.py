import os, sys
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
from step5_analyze_probe_919 import rows

target_10 = [
    "1RB1LA_1LC1RE_1RD1RC_0LA0LH_1LD0RF_---0RC_1LE1LG_1LC1LG",
    "1RB1LA_1LC1RE_1RD1RC_0LA0LH_1LD0RF_---0RC_1LE1LG_0LD1LG",
    "1RB1LA_1LC1RE_1RD1RC_0LA0LH_1LD0RF_---0RC_1LE1LG_0LE1LG",
    "1RB1LA_1LC1RE_1RD1RC_0LA0LH_1LD0RF_---0RC_1LE1LG_0LG1LG",
    "1RB1LA_1LC1RE_1RD1RC_0LA0LH_1LD0RF_---0RC_1LE1LG_0LG1RH",
]

rmap = {r["m"]: r for r in rows}

for m in target_10:
    r = rmap[m]
    print(f"[{r['tag']}] {m}:")
    print("  E:", r["E"])
