import os
import subprocess
import sys

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve, classify_cell
from resolve_g3789 import trace_compact

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"
EXE = os.path.join(BASE_DIR, "strict_tables_cap.exe")
FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS

# 1. Test the new hits from tables_rem_part1_rest.txt up to k=60 at CAPX=0 and CAPX=24
rest_hits_tsv = os.path.join(OUT_DIR, "ckc_hits_rest.tsv")
with open(rest_hits_tsv, "w", encoding="utf-8") as fout:
    for cat, fam, tm, tab in load(os.path.join(OUT_DIR, "tables_rem_part1_rest.txt")):
        hks = [k for k in sorted(tab) if "H" in tab[k][0]]
        if hks:
            fout.write(f"HIT\t{fam}\t{tm}\t| k20=K\n")

for capx in ("0", "24"):
    out_p = os.path.join(OUT_DIR, f"tables_ckc_hits_rest_k60_cap{capx}.txt")
    with open(out_p, "w", encoding="utf-8") as fout:
        p = subprocess.Popen([EXE, rest_hits_tsv, "1", "HIT", "60", capx], stdout=fout, stderr=subprocess.PIPE, creationflags=FLAGS)
        p.communicate()
    print(f"=== Rest hits at KMAX=60, CAPX={capx} ===")
    for cat, fam, tm, tab in load(out_p):
        res, r, traj, per = solve(tab, 60)
        hks = [k for k in sorted(tab) if tab[k][0] == "HH"]
        print(f"  [{res:10s} R={r:2d}] {fam:18s} {tm} | per={per} Hk={hks[:10]} traj={traj[:6]}")

# 2. Check why 1RI0RH_---0RF halted for k=24, 26..36 at CAPX=0 vs CAPX=24 vs CAPX=120
tm_1ri = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI0RH_---0RF"
print(f"\n=== Checking {tm_1ri} across CAPX = 0, 24, 60, 120 ===")
for capx in (0, 24, 60, 120):
    res_list = []
    for k in (20, 23, 24, 25, 26, 30, 35, 40):
        orig_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            kind, dL, I_par, clears = trace_compact(tm_1ri, k, 2 * k + 10, CAPX=capx)
        finally:
            sys.stdout.close()
            sys.stdout = orig_stdout
        res_list.append(f"k={k}:{kind}({dL},{I_par},c={clears})")
    print(f"  CAPX={capx:3d}: " + " ".join(res_list))

# 3. Check the 4 rows that crashed strict_tables_cap.exe using dict-based trace_compact on k=10..25
crashed_tms = [
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RA0LI_---1LD",
    "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0LA0RI_---1RG",
    "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1RG0RI_---1RG",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0RA0LI_---1LD",
]
print("\n=== Checking the 4 array-bounds-crashing rows in trace_compact (k=10..25) ===")
for tm in crashed_tms:
    res_list = []
    for k in range(10, 26):
        orig_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            kind, dL, I_par, clears = trace_compact(tm, k, 2 * k + 10, CAPX=0)
        finally:
            sys.stdout.close()
            sys.stdout = orig_stdout
        res_list.append(f"{k}:{kind}")
    print(f"  {tm}: " + " ".join(res_list))
