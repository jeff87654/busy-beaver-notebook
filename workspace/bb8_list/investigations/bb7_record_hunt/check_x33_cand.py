import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import subprocess, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
RK7 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'

m = "1RB1RA_0RC0RA_0LD1RC_1LE0LF_1LB1LE_1RE1LG_---0LE"
t_args = ['R', 'A', '-', '1', '0', '1', '0', '1', '0', '-']

# 1. Trace from blank tape
p = subprocess.run([RK7, 'trace', m] + t_args + ['50000000', '40'], capture_output=True, text=True, creationflags=0x40)
print("=== Blank-tape trace ===")
for l in p.stdout.strip().splitlines():
    print(" ", l)

# 2. Probe R1, R2, R3(k=1..5) for various b, and E(b=0..25)
cfgs = [
    ([2], 2, 10), ([2], 2, 11),
    ([2], 0, 10), ([2], 0, 11),
]
for k in range(1, 6):
    for b in (20, 21, 22):
        cfgs.append(([1, 2] + [0]*k, 0, b))
for b in range(0, 24):
    cfgs.append(([], 0, b))

inp = ''.join(f"{','.join(map(str, ds)) if ds else '-'} {a} {b}\n" for ds, a, b in cfgs)
p2 = subprocess.run([RK7, 'probe', m] + t_args + ['500000'], input=inp, capture_output=True, text=True, creationflags=0x40)
lines = p2.stdout.strip().splitlines()
print("\n=== Rule probes ===")
for (ds, a, b), res in zip(cfgs, lines):
    print(f"  K({ds}; {a}; {b}) -> {res}")
