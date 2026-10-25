import os
import subprocess
import sys

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve, classify_cell, find_period

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"

# 1. Inspect the 0LI1LC_1LH--- rows in full k=1..36
for name in ("tables_clean_k_231.txt", "tables_clean_k_232.txt"):
    path = os.path.join(OUT_DIR, name)
    rows = load(path)
    for cat, fam, tm, tab in rows:
        if "0LI1LC_1LH---" in tm or "0LI1LD" in tm:
            print(f"\n=== {name}: {fam} {tm} ===")
            for k in sorted(tab):
                print(f"  k={k:2d}: {tab[k]} -> {classify_cell(tab[k])}")
            for pmax in (20, 30):
                for kmin in range(12, 22):
                    per = find_period({k: classify_cell(tab[k]) for k in tab}, kmin, max(tab), pmax=pmax)
                    if per:
                        print(f"  Period from kmin={kmin}: {per}")
                        break

# 2. Check first 10 lines of verify_strict_all.out.txt
vsa_in = os.path.join(BASE_DIR, "verify_strict_all.out.txt")
raw = open(vsa_in, "rb").read()
txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
lines = txt.splitlines()
print(f"\n=== verify_strict_all.out.txt ({len(lines)} lines) first 10 lines ===")
for l in lines[:10]:
    print(" ", l[:120])
tag_counts = {}
for l in lines:
    if "k20=K" in l or "CLEAN_K" in l or "K_CASCADE" in l:
        parts = l.split()
        tag = parts[0] if parts else ""
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
print("Tag counts:", tag_counts)
