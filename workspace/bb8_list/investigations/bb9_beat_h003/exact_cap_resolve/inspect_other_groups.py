import sys
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_beat_h003')
from inspect_post_m5_2 import run_inspect
from solve_rounds import load, classify_cell

reps = [
    ("G2_1RA0RE", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0RE"),
    ("G2_0RE0LH", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0RE0LH"),
    ("G2_1LH0RE", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1LH0RE"),
    ("G3_0LE0LF", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0LE0LF"),
    ("G3_0RG0LF", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0RG0LF"),
    ("G4_1LF0LI", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1LF0LI"),
    ("G4_1RE0LI", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RE0LI"),
    ("G5_0LC1LB", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_0LC1LB"),
    ("G6_1RF1LC", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RF1LC"),
    ("G7_1LD0LI", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD0LI_1LH---"),
    ("G8_1LD1LI", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD1LI_0LH---"),
    ("G9_F2",     "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RI_---0RE_1RH1RB"),
]

# First print their tables from capS1_0.txt, capS1_12.txt, capA_0.txt, capA_12.txt, capN_0.txt, capN_12.txt
maps0 = {}
maps12 = {}
for g in ['capA', 'capS1', 'capS2', 'capN']:
    for _, _, tm, tab in load(f'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_beat_h003/{g}_0.txt'):
        maps0[tm] = tab
    for _, _, tm, tab in load(f'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_beat_h003/{g}_12.txt'):
        maps12[tm] = tab

for name, tm in reps:
    t0 = maps0[tm]
    t12 = maps12[tm]
    print(f"=== {name}: {tm} ===")
    cells0 = []
    diffs = []
    for k in range(1, min(73, max(t0)+1)):
        c0 = t0[k]
        c12 = t12[k]
        s0 = f"{k}:{c0[0]}:{c0[1]}:{c0[3]}" if c0[1]==c0[2] else f"{k}:{c0[0]}:{c0[1]}/{c0[2]}:{c0[3]}"
        cells0.append(s0)
        if c0 != c12:
            diffs.append((k, c0[:4], c12[:4]))
    print("  CAP0 (k=1..36):", " ".join(cells0[:36]))
    print("  CAP0 (k=37..72):", " ".join(cells0[36:72]))
    print(f"  Diffs (CAP0 vs CAP12, total {len(diffs)}):", diffs[:12])
