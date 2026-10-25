import glob
import os
import subprocess
import sys

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve, classify_cell, find_period
from resolve_g3789 import trace_compact

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"

tms = [
    ("STD9", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0LI1LC_1LH---"),
    ("STD9", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0LI1LC_1LH---"),
]

for fam, tm in tms:
    tab = {}
    for k in range(1, 61):
        orig_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            k1, d1, i1, c1 = trace_compact(tm, k, 2 * k + 10, CAPX=0)
            k2, d2, i2, c2 = trace_compact(tm, k, 2 * k + 30, CAPX=0)
        finally:
            sys.stdout.close()
            sys.stdout = orig_stdout
        tab[k] = (k1 + k2, d1, d2, i1, i2)
    res, r, traj, per = solve(tab, 60)
    print(f"=== {fam} {tm} (k=1..60, CAPX=0) ===")
    print(f"  Result: {res} R={r} per={per}")
    print(f"  Traj: {traj}")

# Also check all .tsv files in bb9_beat_h003 and bb9_champ231_accel
for d in [
    BASE_DIR,
    r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel",
]:
    for p in glob.glob(os.path.join(d, "*.tsv")):
        print("Found TSV:", p)
        tags = {}
        with open(p, "rb") as f:
            raw = f.read()
        txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
        for line in txt.splitlines():
            if "k20=K" in line:
                cols = line.split("\t")
                if len(cols) >= 2:
                    t = cols[1]
                    tags[t] = tags.get(t, 0) + 1
        print("  tags with k20=K:", tags)
