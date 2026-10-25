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
    sf = os.path.join(WORKDIR, "tmp_starts_w.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_w.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, str(max_steps), str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    out = res.stdout.strip().split("\t")[1:]
    return list(zip(cfgs, out))

# 1. Exact simulation of G#25, G#33, G#47 from [41]; 9
print("=== 1. Exact trace of G#25 / G#33 / G#47 from [41]; 9 ===")
d, a = 41, 9
step = 0
while d > 0:
    # Determine k = number of decrements and next a
    # Wait: inside 1 K-step of G#25, let's see the exact internal recurrence!
    # For even a: 1 decrement, a' = (3*a + 8)//2
    # Why did a=1 give k=3, a'=18?
    # Notice: if x starts at a:
    # If x is odd: x1 = (3*x + 9)//2 ? Let's check:
    #   a=1 -> x1 = 6 (even)? No, if x1=6, 1 more step gives (3*6+8)//2 = 13 != 18.
    #   Wait: look at the formula we found:
    #   k=1 (a == 0 mod 2): a' = (3*a + 8) // 2
    #   k=2 (a == 3 mod 4): a' = (9*a + 33) // 4
    #   k=3 (a == 1 mod 8): a' = (27*a + 117) // 8
    #   k=4 (a == 13 mod 16): a' = (81*a + 387) // 16
    #   k=5 (a == 21 mod 32): a' = (243*a + 1215) // 32
    #   k=6 (a == 5 mod 64): a' = (729*a + 3843) // 64
    # Look at the recurrence between (k, a'):
    #   For odd x, let x_next = (3*x + 7) // 2:
    #     a=3 (odd) -> x1 = (9+7)//2 = 8 (even!) -> then on even x1, final step is (3*x1 + 9)//2 = (24+9)//2? Wait:
    #     Let's check: 33 - 3*8 = 9; 117 - 3*33 = 18; 387 - 3*117 = 36; 1215 - 3*387 = 54? No, 3843 - 3*1215 = 198?
    #     Wait: look at C_k:
    #     k=1: (3a + 8)/2 -> 3*(a + 3) - 1 / 2
    #     k=2: (9a + 33)/4 -> (9*(a + 3) + 6) / 4
    #     k=3: (27a + 117)/8 -> (27*(a + 3) + 36) / 8
    #     k=4: (81a + 387)/16 -> (81*(a + 3) + 144) / 16
    #     k=5: (243a + 1215)/32 -> (243*(a + 3) + 486) / 32
    #     k=6: (729a + 3843)/64 -> (729*(a + 3) + 1656) / 64? Wait: for a=5, a+3=8, (729*8 + 1512)/64 = (5832 + 1512)/64 = 7344/64 = 114.75, whereas 729*5 + 3843 = 3645 + 3843 = 7488, 7488/64 = 117!
    #     Aha! For a=5, 729*5 + C_6 = 7488 -> 729*(5+3) + (C_6 - 2187) = 5832 + 1656 = 7488!
    #     Wait why 6, 36, 144, 486, 1656?
    #     Let's trace the step-by-step map on x:
    #     When x is odd: x' = (3*x + 7)//2? Wait:
    #     Test a=3: (3*3+7)//2 = 8 (even). Then (3*8+6)//2 = 15!
    #     Test a=1: (3*1+7)//2 = 5 (odd) -> (3*5+7)//2 = 11 (odd) -> (3*11+7)//2 = 20 (even)? No, if it depends on x mod 2:
    #     What if the odd step is x -> (3*x + 11)//2?
    #     Let's check:
    #       k=1 (even a): a' = (3*a + 8)//2
    #       If odd step is x -> (3*x + 9)//2, and final even step is x -> (3*x + 8)//2:
    #       Wait: if first step is x -> (3*x + 9)//2 (when x odd), then:
    #       a=3 -> (9+9)//2 = 9 (odd)? No!
    #     What if first step is x -> (3*x + 8)//2 when x is even, and when x is odd, x -> 3*x + 6 (no division by 2)? No, the denominator is 2^k!
    #     So each of the k steps divides by 2!
    #     Let's find the exact per-decrement map f(x) = (3*x + c) // 2!
    break

# Let's check what happens after 1 decrement in G#25 by comparing [10]; a and [9]; a'!
# Wait: in G#25, why does 1 K-visit do k decrements? Because while b != 0 (the state/parity counter b!), it doesn't match b == B0 = 0!
# Aha!! In kblank_detail and kmap2, we filtered by b == B0 (B0 = 0)!
# When b != 0, it IS visiting K, just with b != 0!
print("Testing G#25 with B0 = -1 (any b) in kmap2!")
tt = T("d")
sf = os.path.join(WORKDIR, "tmp_starts_w.txt")
with open(sf, "w") as f:
    for a in range(1, 10):
        for b in range(4):
            w = word("d", [2, 3], a, b)
            f.write(f"a{a}_b{b} {w} {len(w)} {tt['q']} 1\n")
mf = os.path.join(WORKDIR, "tmp_probe_w.txt")
with open(mf, "w") as f:
    f.write("1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB\n")
cmd = [kmap2_exe, mf] + targs("d") + [sf, "100000", "-1"]
res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
out = res.stdout.strip().split("\t")[1:]
idx = 0
for a in range(1, 10):
    row_s = []
    for b in range(4):
        row_s.append(f"b={b}:{out[idx]}")
        idx += 1
    print(f"  a={a}: " + " | ".join(row_s))
