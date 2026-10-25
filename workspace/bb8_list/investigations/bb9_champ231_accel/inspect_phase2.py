import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

# Let's see what happens between step 61529 and step 67181 in KKHKHK k=3!
tm = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"
tr = parse_tm(tm)

k = 3; N = 6
left_str = "10"*(2*k-1) + "11001"
right_str = "100" + "1100"*N + "1"
full_str = left_str + "1" + right_str
h = len(left_str)
tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
q = 2
e0_count = 0
for step in range(1, 67200):
    b = tape.get(h, 0)
    act = tr[2*q + b]
    if act == "---":
        break
    if int(act[0]): tape[h] = 1
    else: tape.pop(h, None)
    h += 1 if act[1] == "R" else -1
    q = ord(act[2]) - 65
    if step >= 61520 and q == 4 and tape.get(h, 0) == 0:
        e0_count += 1
        if e0_count <= 12 or e0_count >= 130:
            mn, mx = min(min(tape), h), max(max(tape), h)
            # summarize runs of 1s and 0s
            s = "".join(f"[{chr(65+q)}0]" if i == h else str(tape.get(i,0)) for i in range(mn, min(mx+1, mn+70)))
            print(f"e0#{e0_count:3d} step {step:5d} (h={h:4d}, mn={mn:4d}): {s}...")
print(f"Total E0 visits after step 61520: {e0_count}")
