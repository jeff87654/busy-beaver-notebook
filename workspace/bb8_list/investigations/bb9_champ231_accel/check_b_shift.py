import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

for name, tm in [
    ("KHTKHT_231", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LC0RI_1LC---"),
    ("KKTKKT_231", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RI0RG"),
]:
    tr = parse_tm(tm)
    k = 3; N = 6
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    q = 2
    for step in range(1, 5000):
        b = tape.get(h, 0)
        act = tr[2*q + b]
        if act == "---":
            print(f"{name}: HALT at step {step}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        q = ord(act[2]) - 65
        if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1:
            mx = max(tape)
            r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
            print(f"{name} step {step:4d} (h={h}): [E0]{r_str}")
            if step > 500:
                break
