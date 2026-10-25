import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tm = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH"
tr = parse_tm(tm)

# Test [E0] 100 1^6 00 1 00 00 (1100)^b 1^11 0000 1100 1100 1 for b = 0, 1, 2, 3, 4
for b_cnt in [0, 1, 2, 3, 4]:
    s_right = "100" + "1"*6 + "0010000" + "1100"*b_cnt + "1"*11 + "0000110011001"
    tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
    h, q = 0, 4
    for step in range(1, 50000):
        b = tape.get(h, 0)
        act = tr[2*q + b]
        if act == "---":
            print(f"b_cnt={b_cnt}: HALT({chr(65+q)}{b}) at step {step}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1 and step > 500:
            mx = max(tape)
            r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
            if r_str.startswith("100") and "00100" not in r_str[:15]:
                parts = r_str[:-3].split("00")
                print(f"b_cnt={b_cnt} (k={b_cnt+5}): step={step:5d} -> [E0] runs={[len(p) for p in parts]}")
                break
