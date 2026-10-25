import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

exe_path = os.path.join(WORKDIR, "trace_runs.exe")
m25 = "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB"

# 1. Trace [41]; 9 in G#25 using the exact (a, bl) recurrence!
print("=== 1. Exact 41-step atomic trace of [41]; 9 (bl=2) in G#25 ===")
d, a, bl = 41, 9, 2
for step in range(1, 45):
    if d == 0:
        print(f"  Reached d=0: []; a={a}, bl={bl} at atomic step {step-1}!")
        break
    d -= 1
    if bl == 2:
        if a % 2 == 0:
            a, bl = (3*a + 8)//2, 2
        else:
            a, bl = (3*a + 7)//2, 1
    else:
        if a % 2 == 1:
            a, bl = (3*a + 5)//2, 1
        else:
            a, bl = (3*a + 6)//2, 2
    print(f"  Step {step:02d}: d={d:2d}, a={a}, bl={bl}")

# Wait: what happens when d=1 -> d=0 with bl=1 vs bl=2 in G#25?
# Earlier in step7u section 3, we saw:
#   ([1], 1) -> H:200:G0 (here a=1, bl=2 -> tries to go to bl=1 on d=0 and HALTS!)
#   ([2], 1) -> H:593:G0 (here d=2, a=1, bl=2 -> d=1, a=5, bl=1 -> tries to decrement d=1 with bl=1 and HALTS!)
#   ([2], 3) -> K:;15;0  (here d=2, a=3, bl=2 -> d=1, a=8, bl=1 -> since a=8 is EVEN, [1]; 8; (bl=1) goes to []; 15; (bl=2)!)
#   ([3], 1) -> K:;18;0  (here d=3, a=1, bl=2 -> d=2, a=5, bl=1 -> d=1, a=10, bl=1 -> since a=10 is EVEN, [1]; 10; (bl=1) goes to []; 18; (bl=2)!)
#   ([4], 5) -> H:10122:G0 (here d=4, a=5, bl=2 -> reaches d=1 with a ODD and bl=1, and HALTS!)
# Aha!! Whether d=1 -> d=0 has bl=1 or bl=2, it ALWAYS HALTS (either during d=1 -> d=0 if bl'=1, or at []; a; bl=2 where E(a) = HALT for all a)!

# 2. Now let's run trace_runs.exe on G#23, G#24, and G#27 to see their exact atomic (a, bl) rules!
m23 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RD"
print("\n=== 2. G#23 trace_runs on [10]; a for a=1,2,3,4,6,10 ===")
for a in [1, 2, 3, 4, 6, 10]:
    w0 = word("d", [10], a, 0)
    res = subprocess.run([exe_path, m23] + targs("d") + [w0], capture_output=True, text=True, creationflags=0x40)
    print(f"  a={a}:")
    for l in res.stdout.strip().split("\n"):
        print("    " + l)

m24 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RE"
print("\n=== 3. G#24 trace_runs on [10]; a for a=1,2,3,4,5,7 ===")
for a in [1, 2, 3, 4, 5, 7]:
    w0 = word("d", [10], a, 0)
    res = subprocess.run([exe_path, m24] + targs("d") + [w0], capture_output=True, text=True, creationflags=0x40)
    print(f"  a={a}:")
    for l in res.stdout.strip().split("\n"):
        print("    " + l)
