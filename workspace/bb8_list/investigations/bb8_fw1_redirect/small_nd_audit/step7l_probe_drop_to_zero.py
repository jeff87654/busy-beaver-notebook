import os, sys, subprocess
FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
AUDIT_DIR = os.path.join(FW1_DIR, "small_nd_audit")
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

KMAP2 = os.path.join(FW1_DIR, "kmap2.exe")

def probe_machine(tag, m, cfgs):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(AUDIT_DIR, "tmp_sf.txt")
    mf = os.path.join(AUDIT_DIR, "tmp_mf.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    with open(mf, "w") as f:
        f.write(m + "\n")
    p = subprocess.run([KMAP2, mf] + targs(tag) + [sf, "200000", str(B0)],
                       capture_output=True, text=True, creationflags=0x40)
    cols = p.stdout.strip().split("\t")[1:]
    for (ds, a), c in zip(cfgs, cols):
        print(f"  ({ds}, a={a}) -> {c}")

print("Probing [e] 1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1RH1LF_---0RA_1LB1LH:")
probe_machine("e", "1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1RH1LF_---0RA_1LB1LH", [
    ([2, 1, 0], 3), ([2, 1, 0], 4),
    ([2, 2, 0], 3), ([2, 2, 0], 4),
    ([2, 3, 0], 3), ([2, 3, 0], 4),
    ([2, 4, 0], 3), ([2, 4, 0], 4),
    ([2, 5, 0], 3), ([2, 5, 0], 4),
    ([1, 0], 3), ([1, 0], 4),
    ([2, 0], 3), ([2, 0], 4),
    ([3, 0], 3), ([3, 0], 4),
])

print("\nProbing [i] 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF:")
probe_machine("i", "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF", [
    ([2, 1, 0], 3), ([2, 1, 0], 4),
    ([2, 2, 0], 3), ([2, 2, 0], 4),
    ([2, 3, 0], 3), ([2, 3, 0], 4),
    ([2, 5, 0], 3), ([2, 5, 0], 4),
    ([1, 0], 3), ([1, 0], 4),
    ([2, 0], 3), ([2, 0], 4),
    ([3, 0], 3), ([3, 0], 4),
])
