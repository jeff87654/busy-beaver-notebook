import os, glob
from collections import Counter

for root, dirs, files in os.walk(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations"):
    for f in files:
        if "verify_strict" in f or "accel_champ" in f:
            print("Found:", os.path.join(root, f))

def has_reachable_halt(tm):
    parts = tm.split('_')
    # states A..I are 0..8
    # check if any state has --- and is referenced as a next state
    referenced = {'A', 'B', 'C'}
    changed = True
    while changed:
        changed = False
        for idx, p in enumerate(parts):
            st = chr(ord('A') + idx)
            if st in referenced:
                for b in (0, 3):
                    nxt = p[b+2]
                    if nxt != '-' and nxt not in referenced:
                        referenced.add(nxt)
                        changed = True
    for idx, p in enumerate(parts):
        st = chr(ord('A') + idx)
        if st in referenced and ('---' in (p[:3], p[3:6])):
            return True
    return False

for name, path in [
    ("231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
    ("232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
]:
    tot = 0
    reach = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("CLEAN_K") and "| k20=K" in line:
                tot += 1
                tm = line.split()[1]
                if has_reachable_halt(tm):
                    reach += 1
    print(f"{name}: CLEAN_K with k20=K = {tot}, with reachable --- = {reach}")
