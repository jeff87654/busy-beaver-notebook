import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

# Wait: in G#25, G#23, G#24, G#27, why did a=1; b=... in step7x do multiple steps?
# Because when a=0 or a=1, what is the OTHER state or b value?
# Wait: we don't even need to guess! We have the exact closed-form laws for b=0!
# Let's verify the closed-form laws for G#25, G#23, G#24, and G#27 and simulate them!

# 1. Simulate G#25 / G#33 / G#47 from [41]; 9
print("=== 1. Exact simulation of G#25 / G#33 / G#47 from [41]; 9 ===")
def step_G25(d, a):
    # If a is even (a = 2m): k = 1, a' = 3m + 4
    if a % 2 == 0:
        k = 1
        a_next = 3 * (a // 2) + 4
    else:
        # Let's check odd a = 2m + 1:
        # m=1 (a=3): k=2, a'=15
        # m=0 (a=1): k=3, a'=18
        # m=4 (a=9): k=3, a'=45
        # m=6 (a=13): k=4, a'=90
        # m=10 (a=21): k=5, a'=198
        # m=2 (a=5): k=6, a'=117
        # Notice: for odd a, let x = (3*a + 3) // 2 (which is 3m + 3):
        # Wait: for a=3 (m=1), x = 6 (even) -> k=2, a' = (9*6 - 24)/2 = 15?
        # Let's check:
        # k >= 2: a' is a multiple of 3! Specifically:
        # k=2 (a = 4j + 3): a' = 9j + 15
        # k=3 (a = 8j + 1): a' = 27j + 18
        # k=4 (a = 16j + 13): a' = 81j + 90
        # k=5 (a = 32j + 21): a' = 243j + 198
        # k=6 (a = 64j + 5): a' = 729j + 117
        # Look at how j is obtained by repeated halving:
        # Start with m = (a - 1) // 2, k = 1:
        # Step 1 (from odd a = 2m+1): if m is odd (m = 2j+1, so a = 4j+3), k=2, a' = 9j + 15!
        # If m is even (m = 2m1): first step sends m -> m1 = (3*m + 2)//2?
        # Let's check:
        #   m=0 (a=1): (3*0+2)//2 = 1 (odd, j=0) -> k=3, a' = 18!
        #   m=4 (a=9): (3*4+2)//2 = 7 (odd, j=3) -> k=3, a' = 9*3 + 18 = 45!
        #   m=6 (a=13): (3*6+2)//2 = 10 (even) -> next step (3*10+2)//2 = 16? No, for k>=3:
        #   If we use x -> (3*x + 2)//2 while x is even, starting from x = m:
        #   - m=0: 0 (even) -> 1 (odd)! (1 even step -> k=3, x_odd = 1 -> a' = 9*1 + 9 = 18!)
        #   - m=4: 4 (even) -> 7 (odd)! (1 even step -> k=3, x_odd = 7 -> a' = 9*7 - 18? Wait: 9*(7+1)/2 = 36? No: (9*7 + 27)//2 = 45!)
        #   - m=6: 6 (even) -> 10 (even) -> 16? No, why did m=6 stop at k=4 with a'=90, while m=2 stopped at k=6 with a'=117?!
        #   Because the step on m is: while m is even, m = (3*m + 2)//2? Wait: for m=2, 2 -> 4 -> 7 (that would be 2 even steps, k=4, not k=6!).
        #   For m=2 to take 4 steps and m=6 to take 2 steps, the step on even m must be m -> (3*m + 4)//2 or (3*m + 6)//2!
        #   Test m -> (3*m + 6)//2 on even m:
        #     m=0: 0 -> 3 (odd! 1 step, k=3). And (9*3 + 9)/2 = 18!
        #     m=4: 4 -> 9 (odd! 1 step, k=3). And (9*9 + 9)/2 = 45!
        #     m=6: 6 -> 12 (even) -> 21 (odd! 2 steps, k=4). And (9*21 - 9)/2 = 90!
        #     m=10: 10 -> 18 (even) -> 30 (even) -> 48? No, 10 -> 18 -> 30 -> 48 -> ...
        #   Test m -> (3*m + 2)//2 vs (3*m - 2)//2:
        #   Look at the binary residues of a where k = 2, 3, 4, 5, 6:
        #     k=1: a == 0 (mod 2)   [a + 11 == 11 (mod 2), v2(a+11) = 0]
        #     k=2: a == 3 (mod 4)   [a + 11 == 14 == 2 (mod 4), v2(a+11) = 1]
        #     k=3: a == 1 (mod 8)   [a + 11 == 12 == 4 (mod 8), v2(a+11) = 2]
        #     k=4: a == 13 (mod 16) [a + 11 == 24 == 8 (mod 16), v2(a+11) = 3]
        #     k=5: a == 21 (mod 32) [a + 11 == 32 (mod 32), v2(a+11) >= 5? No: 21 + 11 = 32, 5 + 11 = 16!]
        #     WAIT A SECOND! Look at a + 11:
        #     - a = 2m: a + 11 is ODD -> v2(a + 11) = 0 -> k = 1!
        #     - a = 3 (mod 4): a + 11 == 2 (mod 4) -> v2(a + 11) = 1 -> k = 2!
        #     - a = 1 (mod 8): a + 11 == 4 (mod 8) -> v2(a + 11) = 2 -> k = 3!
        #     - a = 13 (mod 16): a + 11 == 8 (mod 16) -> v2(a + 11) = 3 -> k = 4!
        #     Wait: why did a=21 have k=5 and a=5 have k=6?
        #     What number X has:
        #       3 + X == 2 (mod 4)   -> X == 3 (mod 4)
        #       1 + X == 4 (mod 8)   -> X == 3 (mod 8)
        #       13 + X == 8 (mod 16) -> X == 11 (mod 16)
        #       21 + X == 16 (mod 32)-> X == 27 (mod 32)
        #       5 + X == 32 (mod 64) -> X == 27 (mod 64)!
        #     27! Wait: 3 + 27 = 30 == 2 (mod 4); 1 + 27 = 28 == 4 (mod 8); 13 + 27 = 40 == 8 (mod 16); 21 + 27 = 48 == 16 (mod 32); 5 + 27 = 32 == 32 (mod 64)!
        #     What is 27, 91, ... in 2-adic integers?!
        #     In 2-adic integers, look at the sequence 3, 3, 11, 27, 27, 91, ...:
        #     Wait: 3*5 + 11 = 26? No: 5*5 + 2 = 27? No: 3*a + 7!
        pass

# Let's just trace [41]; 9 in G#25 directly using kmap2 step by step!
m25 = "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB"
tt = T("d")
d, a = 41, 9
step_num = 0
while True:
    step_num += 1
    sf = os.path.join(WORKDIR, "tmp_starts_z.txt")
    w = word("d", [d] if d > 0 else [], a, 0)
    with open(sf, "w") as f:
        f.write(f"c0 {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_z.txt")
    with open(mf, "w") as f:
        f.write(m25 + "\n")
    cmd = [kmap2_exe, mf] + targs("d") + [sf, "50000000", "0"]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    ans = res.stdout.strip().split("\t")[1]
    print(f"  Step {step_num:02d}: [{d}]; {a} -> {ans}")
    if not ans.startswith("K:"):
        break
    body = ans[2:].split(";")
    ds_str = body[0]
    a = int(body[1])
    d = int(ds_str) if ds_str else 0
