import os
import sys

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve, classify_cell, find_period
from resolve_g3789 import trace_compact

OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"

for fn in ("tables_rem_part1.txt", "tables_rem_part2.txt"):
    rows = load(os.path.join(OUT_DIR, fn))
    for cat, fam, tm, tab in rows:
        hks = [k for k in sorted(tab) if "H" in tab[k][0]]
        if not hks:
            continue
        print(f"\n=== {fam} {tm} (Hk={hks}) ===")
        for k in range(1, 37):
            print(f"  k={k:2d}: {tab[k]} -> {classify_cell(tab[k])}")
        break
