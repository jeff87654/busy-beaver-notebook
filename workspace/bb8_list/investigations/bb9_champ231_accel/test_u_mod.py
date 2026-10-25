import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tm = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH"
tr = parse_tm(tm)

# Test [E0] 100 1^u 00 1 (00)^m 1100 1100 1 for m = 1, 2, 3, 4 and u = 6, 12
for m in [1, 2, 3, 4]:
    for u in [6, 12]:
        s_right = "100" + "1"*u + "001" + "00"*m + "110011001"
        tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
        h, q = 0, 4
        for step in range(1, 50000):
            b = tape.get(h, 0)
            act = tr[2*q + b]
            if act == "---":
                print(f"m={m}, u={u:2d}: HALT({chr(65+q)}{b}) at step {step}")
                break
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == 'R' else -1
            q = ord(act[2]) - 65
            if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1 and step > 3*u*u + 20*u:
                mx = max(tape)
                r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
                if r_str.startswith("100") or r_str.startswith("1100"):
                    parts = r_str[:-3].split("00")
                    print(f"m={m}, u={u:2d}: step={step:5d} -> [E0] runs={[len(p) for p in parts]}")
                    break
