import os, sys
os.environ["PATH"] = r"C:\msys64\ucrt64\bin;" + os.environ.get("PATH", "")
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from pathlib import Path
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

p1 = Path(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv')
p2 = Path(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv')

by_m = {}
for p in (p1, p2):
    for line in p.read_text().splitlines()[1:]:
        if not line.strip() or line.startswith('#'): continue
        parts = line.split('\t')
        if len(parts) >= 7:
            by_m[parts[0]] = parts

# Let's check NEW_MULTI on [0^k; a; 1] first!
NEW_MULTI = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
T_nm = kl.tmpl(NEW_MULTI, by_m[NEW_MULTI][4])
print("=== NEW_MULTI on [0^k; a; 1] ===")
for k in range(0, 4):
    for a in range(1, 5):
        ev = kl.run(NEW_MULTI, [0]*k, a, 1, steps=500000, nchg=2, maxl=10, T=T_nm, pall=0)
        k_evs = [e for e in ev if e[0] in ('K', 'H')]
        print(f"  k={k}, a={a}: {k_evs[:3]}")
