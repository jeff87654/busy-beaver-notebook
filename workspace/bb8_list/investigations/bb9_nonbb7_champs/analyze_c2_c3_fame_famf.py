import sys, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

# 1. Trace C2_L1 macro steps from blank tape
print("=== 1. Tracing C2_L1 from blank tape ===")
trans_c2 = parse_tm("1RB---_1LC1LE_1LD0LC_0RE0LA_0LF0RF_1RF1RG_1LB1RB")
tape = {}; head = 0; state = 0
for step in range(1, 5000):
    v = tape.get(head, 0)
    t = trans_c2[(state, v)]
    if t is None:
        print(f"HALT at {step-1}")
        break
    w, d, ns = t
    if w == 0: tape.pop(head, None)
    else: tape[head] = 1
    head += d; state = ns
    if state == 6 and tape.get(head, 0) == 1 and head >= max(tape.keys()):
        print(f"  step {step:5d}: {format_tape(tape, head, state)}")

# 2. Trace C3_1 from step 910 config with k_twos = 0 and k_twos = 1
print("\n=== 2. Tracing C3_1 on k_twos = 0 ===")
trans_c3 = parse_tm("1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE")
cfg = "101001010B[1]10001000101"
tape = {}; pos = 0; i = 0
while i < len(cfg):
    if cfg[i].isalpha():
        state = ord(cfg[i]) - ord('A')
        if int(cfg[i+2]) == 1: tape[pos] = 1
        head = pos; pos += 1; i += 4
    else:
        if int(cfg[i]) == 1: tape[pos] = 1
        pos += 1; i += 1

for step in range(1, 2000):
    v = tape.get(head, 0)
    t = trans_c3[(state, v)]
    if t is None:
        print(f"HALT at {step-1}: {format_tape(tape, head, state)}")
        break
    w, d, ns = t
    if w == 0: tape.pop(head, None)
    else: tape[head] = 1
    head += d; state = ns
    ft = format_tape(tape, head, state)
    if "0000" in ft and state in (1, 2, 3):
        if step < 600:
            print(f"  step {step:4d}: {ft}")

# 3. Check closest machines in hits_triage7.tsv / dl2_out / dl3_hits to FamE and FamF
FamE = "1RB0RA_1LC1RF_1RE0LD_0LC0LE_1RA---_1RD0LG_0RF0RG"
FamF = "1RB1LC_0LA0LD_1LA1LF_1RE0RB_1RF1LE_1RG0RC_0RF---"

def slot_dist(m1, m2):
    s1 = m1.split('_'); s2 = m2.split('_')
    d = 0
    for a, b in zip(s1, s2):
        if a[:3] != b[:3]: d += 1
        if a[3:] != b[3:]: d += 1
    return d

all_machines = set()
with open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\hits_triage7.tsv') as f:
    for line in f:
        if line.strip() and not line.startswith('machine'):
            all_machines.add(line.split('\t')[0])
with open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\machines.txt') as f:
    for line in f:
        if line.strip():
            all_machines.add(line.strip())

print("\n=== 3. Closest machines to FamE and FamF ===")
for name, target in [("FamE", FamE), ("FamF", FamF)]:
    best = sorted([(slot_dist(target, m), m) for m in all_machines])[:5]
    print(f"Closest to {name} ({target}):")
    for d, m in best:
        print(f"  dist={d}: {m}")
