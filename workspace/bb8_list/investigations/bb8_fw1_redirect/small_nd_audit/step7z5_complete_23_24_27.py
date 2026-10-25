import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

def probe_configs(tag, m, cfgs, max_steps=1000000):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, "tmp_starts_z5.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_z5.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, str(max_steps), str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    out = res.stdout.strip().split("\t")[1:]
    return list(zip(cfgs, out))

m23 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RD"
m24 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RE"

print("=== 1. G#24 [2, 0, d]; a underflow probes ===")
cfgs_24 = [([2, 0, d], a) for a in [1, 3, 5, 7, 11, 15, 23] for d in [1, 2, 3, 4]] + [([1, 0, d], a) for a in [1, 3, 5, 7, 15] for d in [1, 2, 3]]
for cfg, ans in probe_configs("d", m24, cfgs_24):
    print(f"  {cfg} -> {ans}")

print("\n=== 2. G#23 [2, 0, d]; a underflow probes ===")
cfgs_23 = [([2, 0, d], a) for a in [2, 4, 6, 8, 10, 14] for d in [1, 2, 3]] + [([1, 0, d], a) for a in [2, 4, 6, 8, 10] for d in [1, 2, 3]]
for cfg, ans in probe_configs("d", m23, cfgs_23):
    print(f"  {cfg} -> {ans}")
