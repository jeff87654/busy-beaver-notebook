import os
import subprocess
import sys
import time

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"
EXE = os.path.join(BASE_DIR, "strict_tables_cap.exe")
FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS


def has_reachable_halt(tm):
    parts = tm.split("_")
    if len(parts) != 9:
        return False
    adj = {}
    halt_states = set()
    for q, p in enumerate(parts):
        adj[q] = set()
        for b in (0, 1):
            tr = p[b * 3 : b * 3 + 3]
            if tr == "---":
                halt_states.add(q)
            else:
                nxt = ord(tr[2]) - ord("A")
                if 0 <= nxt < 9:
                    adj[q].add(nxt)
    # BFS from state C (2) and state A (0)
    vis = {0, 2}
    stack = [0, 2]
    while stack:
        u = stack.pop()
        for v in adj.get(u, ()):
            if v not in vis:
                vis.add(v)
                stack.append(v)
    return bool(vis & halt_states)


already_tested = set()
for fname in (
    "tables_clean_k_231.txt",
    "tables_clean_k_232.txt",
    "tables_cascade_231.txt",
    "tables_cascade_232.txt",
):
    fpath = os.path.join(OUT_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split("\t")
                if len(parts) >= 3:
                    already_tested.add(parts[2])

print(f"Already tabulated in 231/232 CLEAN_K+CASCADE: {len(already_tested)} machines")

filtered_tsv = os.path.join(OUT_DIR, "filtered_remaining_ckc.tsv")
kept = 0
skipped_unreach = 0
skipped_done = 0
with open(filtered_tsv, "w", encoding="utf-8") as fout:
    for name, has_fam, cats in [
        ("std9_exact_231.tsv", False, {"CLEAN_K", "CASCADE"}),
        ("std9_exact_232.tsv", False, {"CLEAN_K", "CASCADE"}),
        ("search_arch_a_d.tsv", True, {"K_CASCADE"}),
    ]:
        c_kept = 0
        with open(os.path.join(BASE_DIR, name), "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if "| k20=K" not in line:
                    continue
                parts = line.split()
                cat = parts[0]
                if cat not in cats:
                    continue
                fam = parts[1] if has_fam else "STD9"
                tm = parts[2] if has_fam else parts[1]
                if tm in already_tested:
                    skipped_done += 1
                    continue
                if not has_reachable_halt(tm):
                    skipped_unreach += 1
                    continue
                already_tested.add(tm)
                fout.write(f"REM_CKC\t{fam}\t{tm}\t| k20=K\n")
                kept += 1
                c_kept += 1
        print(f"  {name}: kept {c_kept} new machines with reachable halt")

print(f"Total kept={kept}, skipped_done={skipped_done}, skipped_unreach={skipped_unreach}")
